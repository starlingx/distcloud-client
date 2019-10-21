# Copyright (c) 2017 Ericsson AB.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Copyright (c) 2017-2019 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import getpass
import os
import yaml

from osc_lib.command import command

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions
from dcmanagerclient import utils


def format(subcloud=None):
    columns = (
        'id',
        'name',
        'management',
        'availability',
        'deploy status',
        'sync'
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.management_state,
            subcloud.availability_status,
            subcloud.deploy_status,
            subcloud.sync_status
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def detail_format(subcloud=None):
    columns = (
        'id',
        'name',
        'description',
        'location',
        'software_version',
        'management',
        'availability',
        'deploy_status',
        'management_subnet',
        'management_start_ip',
        'management_end_ip',
        'management_gateway_ip',
        'systemcontroller_gateway_ip',
        'created_at',
        'updated_at',
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.description,
            subcloud.location,
            subcloud.software_version,
            subcloud.management_state,
            subcloud.availability_status,
            subcloud.deploy_status,
            subcloud.management_subnet,
            subcloud.management_start_ip,
            subcloud.management_end_ip,
            subcloud.management_gateway_ip,
            subcloud.systemcontroller_gateway_ip,
            subcloud.created_at,
            subcloud.updated_at,
        )

        for listitem, sync_status in enumerate(subcloud.endpoint_sync_status
                                               ):
            added_field = (sync_status['endpoint_type'] +
                           "_sync_status",)
            added_value = (sync_status['sync_status'],)
            columns += tuple(added_field)
            data += tuple(added_value)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class AddSubcloud(base.DCManagerShowOne):
    """Add a new subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, parsed_args):
        parser = super(AddSubcloud, self).get_parser(parsed_args)

        parser.add_argument(
            '--bootstrap-address',
            required=True,
            help='IP address for initial subcloud controller.'
        )

        parser.add_argument(
            '--bootstrap-values',
            required=True,
            help='YAML file containing subcloud configuration settings. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--deploy-playbook',
            required=False,
            help='An optional ansible playbook to be run after the subcloud '
                 'has been successfully bootstrapped. It will be run with the '
                 'subcloud as the target and authentication is '
                 'handled automatically. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--deploy-values',
            required=False,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
        )

        parser.add_argument(
            '--subcloud-password',
            required=False,
            help='sysadmin password of the subcloud to be configured, '
                 'if not provided you will be prompted.'
        )

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_manager
        kwargs = dict()
        kwargs['bootstrap-address'] = parsed_args.bootstrap_address

        # Load the configuration from the bootstrap yaml file
        filename = parsed_args.bootstrap_values
        stream = utils.get_contents_if_file(filename)
        kwargs.update(yaml.safe_load(stream))

        # Load the the deploy playbook yaml file
        if parsed_args.deploy_playbook is not None:
            if parsed_args.deploy_values is None:
                error_msg = "Error: Deploy playbook cannot be specified " \
                            "when the deploy values file has not been " \
                            "specified."
                raise exceptions.DCManagerClientException(error_msg)
            filename = parsed_args.deploy_playbook
            stream = utils.get_contents_if_file(filename)
            kwargs['deploy_playbook'] = yaml.safe_load(stream)

        # Load the configuration from the deploy values yaml file
        if parsed_args.deploy_values is not None:
            if parsed_args.deploy_playbook is None:
                error_msg = "Error: Deploy values cannot be specified " \
                            "when a deploy playbook has not been specified."
                raise exceptions.DCManagerClientException(error_msg)

            filename = parsed_args.deploy_values
            if os.path.isdir(filename):
                error_msg = "Error: %s is a directory." % filename
                raise exceptions.DCManagerClientException(error_msg)
            try:
                with open(filename, 'rb') as stream:
                    kwargs['deploy_values'] = yaml.safe_load(stream)
            except Exception:
                error_msg = "Error: Could not open file %s." % filename
                raise exceptions.DCManagerClientException(error_msg)

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.subcloud_password is not None:
            kwargs['subcloud_password'] = parsed_args.subcloud_password
        else:
            while True:
                password = getpass.getpass(
                    "Enter the sysadmin password for the subcloud: ")
                if len(password) < 1:
                    print("Password cannot be empty")
                    continue

                confirm = getpass.getpass(
                    "Re-enter sysadmin password to confirm: ")
                if password != confirm:
                    print("Passwords did not match")
                    continue
                kwargs["subcloud_password"] = password
                break

        return dcmanager_client.subcloud_manager.add_subcloud(**kwargs)


class ListSubcloud(base.DCManagerLister):
    """List subclouds."""

    def _get_format_function(self):
        return format

    def get_parser(self, parsed_args):
        parser = super(ListSubcloud, self).get_parser(parsed_args)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_manager
        return dcmanager_client.subcloud_manager.list_subclouds()


class ShowSubcloud(base.DCManagerShowOne):
    """Show the details of a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, parsed_args):
        parser = super(ShowSubcloud, self).get_parser(parsed_args)

        parser.add_argument(
            'subcloud',
            help='Name or ID of subcloud to view the details.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        return dcmanager_client.subcloud_manager.subcloud_detail(subcloud_ref)


class DeleteSubcloud(command.Command):
    """Delete subcloud details from the database."""

    def get_parser(self, prog_name):
        parser = super(DeleteSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to delete.'
        )
        return parser

    def take_action(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        try:
            dcmanager_client.subcloud_manager.delete_subcloud(subcloud_ref)
        except Exception as e:
            print(e)
            error_msg = "Unable to delete subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class UnmanageSubcloud(base.DCManagerShowOne):
    """Unmanage a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(UnmanageSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to unmanage.'
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        kwargs = dict()
        kwargs['management-state'] = 'unmanaged'
        try:
            return dcmanager_client.subcloud_manager.update_subcloud(
                subcloud_ref, **kwargs)
        except Exception as e:
            print(e)
            error_msg = "Unable to unmanage subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class ManageSubcloud(base.DCManagerShowOne):
    """Manage a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(ManageSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to manage.'
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        kwargs = dict()
        kwargs['management-state'] = 'managed'
        try:
            return dcmanager_client.subcloud_manager.update_subcloud(
                subcloud_ref, **kwargs)
        except Exception as e:
            print(e)
            error_msg = "Unable to manage subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class UpdateSubcloud(base.DCManagerShowOne):
    """Update attributes of a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(UpdateSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to update.'
        )

        parser.add_argument(
            '--description',
            required=False,
            help='Description of subcloud.'
        )

        parser.add_argument(
            '--location',
            required=False,
            help='Location of subcloud.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        kwargs = dict()
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.location:
            kwargs['location'] = parsed_args.location
        if len(kwargs) == 0:
            error_msg = "Nothing to update"
            raise exceptions.DCManagerClientException(error_msg)

        try:
            return dcmanager_client.subcloud_manager.update_subcloud(
                subcloud_ref, **kwargs)
        except Exception as e:
            print(e)
            error_msg = "Unable to update subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)
