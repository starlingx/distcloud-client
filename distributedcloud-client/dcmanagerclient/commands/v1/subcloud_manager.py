# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2023 Wind River Systems, Inc.
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

import base64
import os
import six

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
        'sync',
        'backup status',
        'backup datetime'
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.management_state,
            subcloud.availability_status,
            subcloud.deploy_status,
            subcloud.sync_status,
            subcloud.backup_status,
            subcloud.backup_datetime,
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
        'group_id',
        'created_at',
        'updated_at',
        'backup_status',
        'backup_datetime'
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
            subcloud.group_id,
            subcloud.created_at,
            subcloud.updated_at,
            subcloud.backup_status,
            subcloud.backup_datetime
        )

        for _listitem, sync_status in enumerate(subcloud.endpoint_sync_status):
            added_field = (sync_status['endpoint_type'] +
                           "_sync_status",)
            added_value = (sync_status['sync_status'],)
            columns += tuple(added_field)
            data += tuple(added_value)

        if subcloud.oam_floating_ip != "unavailable":
            columns += ('oam_floating_ip',)
            data += (subcloud.oam_floating_ip,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class AddSubcloud(base.DCManagerShowOne):
    """Add a new subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(AddSubcloud, self).get_parser(prog_name)

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
            '--deploy-config',
            required=False,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
        )

        parser.add_argument(
            '--install-values',
            required=False,
            help='YAML file containing subcloud variables required for remote '
                 'install playbook.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be configured, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            '--bmc-password',
            required=False,
            help='bmc password of the subcloud to be configured, '
                 'if not provided you will be prompted. This parameter is only'
                 ' valid if the --install-values are specified.'
        )

        parser.add_argument(
            '--group',
            required=False,
            help='Name or ID of subcloud group.'
        )

        parser.add_argument(
            '--migrate',
            required=False,
            action='store_true',
            help='Migrate a subcloud from another distributed cloud.'
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_manager
        files = dict()
        data = dict()
        data['bootstrap-address'] = parsed_args.bootstrap_address

        # Get the install values yaml file
        if parsed_args.install_values is not None:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = "install-values does not exist: %s" % \
                            parsed_args.install_values
                raise exceptions.DCManagerClientException(error_msg)
            files['install_values'] = parsed_args.install_values

        # Get the bootstrap values yaml file
        if not os.path.isfile(parsed_args.bootstrap_values):
            error_msg = "bootstrap-values does not exist: %s" % \
                        parsed_args.bootstrap_values
            raise exceptions.DCManagerClientException(error_msg)
        files['bootstrap_values'] = parsed_args.bootstrap_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config is not None:
            if parsed_args.migrate:
                error_msg = "migrate with deploy-config is not allowed"
                raise exceptions.DCManagerClientException(error_msg)

            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = "deploy-config does not exist: %s" % \
                            parsed_args.deploy_config
                raise exceptions.DCManagerClientException(error_msg)
            files['deploy_config'] = parsed_args.deploy_config

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.sysadmin_password is not None:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8"))
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8"))

        if parsed_args.install_values is not None:
            if parsed_args.bmc_password is not None:
                data['bmc_password'] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8"))
            else:
                password = utils.prompt_for_password('bmc')
                data["bmc_password"] = base64.b64encode(
                    password.encode("utf-8"))

        if parsed_args.group is not None:
            data['group_id'] = parsed_args.group

        if parsed_args.migrate:
            data['migrate'] = 'true'

        return dcmanager_client.subcloud_manager.add_subcloud(files=files,
                                                              data=data)


class ListSubcloud(base.DCManagerLister):
    """List subclouds."""

    def _get_format_function(self):
        return format

    def get_parser(self, prog_name):
        parser = super(ListSubcloud, self).get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_manager
        return dcmanager_client.subcloud_manager.list_subclouds()


class ShowSubcloud(base.DCManagerShowOne):
    """Show the details of a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(ShowSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of subcloud to view the details.'
        )

        parser.add_argument(
            '-d', '--detail',
            action='store_true',
            help="Show additional details for a subcloud"
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        if parsed_args.detail:
            return dcmanager_client.subcloud_manager.\
                subcloud_additional_details(subcloud_ref)
        else:
            return dcmanager_client.subcloud_manager.\
                subcloud_detail(subcloud_ref)


class ShowSubcloudError(command.Command):
    """Show the error of the last failed operation."""

    def get_parser(self, prog_name):
        parser = super(ShowSubcloudError, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of subcloud to view the errors details.'
        )
        return parser

    def take_action(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        ret = dcmanager_client.subcloud_manager.subcloud_detail(subcloud_ref)
        data = ret[0].error_description
        print(''.join(data))


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
                subcloud_ref, files=None, data=kwargs)
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

        parser.add_argument(
            '--force',
            required=False,
            action='store_true',
            help='Disregard subcloud availability status, intended for \
                  some upgrade recovery scenarios.'
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        kwargs = dict()
        kwargs['management-state'] = 'managed'
        if parsed_args.force:
            kwargs['force'] = 'true'

        try:
            return dcmanager_client.subcloud_manager.update_subcloud(
                subcloud_ref, files=None, data=kwargs)
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

        parser.add_argument(
            '--group',
            required=False,
            help='Name or ID of subcloud group.'
        )

        parser.add_argument(
            '--admin-subnet',
            required=False,
            help='Admin subnet of subcloud.'
        )

        parser.add_argument(
            '--admin-gateway-ip',
            required=False,
            help='Admin gateway ip of subcloud.'
        )

        parser.add_argument(
            '--admin-start-address',
            required=False,
            help='Admin start address of subcloud.'
        )

        parser.add_argument(
            '--admin-end-address',
            required=False,
            help='Admin end address of subcloud.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be updated, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            '--bootstrap-address',
            required=False,
            help='bootstrap address of the subcloud to be updated, '
        )

        parser.add_argument(
            '--install-values',
            required=False,
            help='YAML file containing subcloud variables required for remote '
                 'install playbook.'
        )

        parser.add_argument(
            '--bmc-password',
            required=False,
            help='bmc password of the subcloud to be configured, if not '
                 'provided you will be prompted. This parameter is only'
                 ' valid if the --install-values are specified.'
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        files = dict()
        data = dict()
        update_admin_network = False

        if parsed_args.description:
            data['description'] = parsed_args.description
        if parsed_args.location:
            data['location'] = parsed_args.location
        if parsed_args.group:
            data['group_id'] = parsed_args.group
        if parsed_args.admin_subnet:
            data['admin_subnet'] = parsed_args.admin_subnet
            update_admin_network = True
        if parsed_args.admin_gateway_ip:
            data['admin_gateway_ip'] = parsed_args.admin_gateway_ip
            update_admin_network = True
        if parsed_args.admin_start_address:
            data['admin_start_address'] = parsed_args.admin_start_address
            update_admin_network = True
        if parsed_args.admin_end_address:
            data['admin_end_address'] = parsed_args.admin_end_address
            update_admin_network = True
        if parsed_args.bootstrap_address:
            data['bootstrap_address'] = parsed_args.bootstrap_address

        # Semantic check if the required arguments for updating admin network
        if update_admin_network:
            if not parsed_args.admin_subnet:
                error_msg = ("Argument --admin-subnet is required for admin "
                             "network reconfiguration request.")
                raise exceptions.DCManagerClientException(error_msg)

            if not parsed_args.admin_gateway_ip:
                error_msg = ("Argument --admin-gateway-ip is required for "
                             "admin network reconfiguration request.")
                raise exceptions.DCManagerClientException(error_msg)

            if not parsed_args.admin_start_address:
                error_msg = ("Argument --admin-start-address is required for "
                             "admin network reconfiguration request.")
                raise exceptions.DCManagerClientException(error_msg)

            if not parsed_args.admin_end_address:
                error_msg = ("Argument --admin-end-address is required for "
                             "admin network reconfiguration request.")
                raise exceptions.DCManagerClientException(error_msg)

            if not parsed_args.bootstrap_address:
                error_msg = ("Argument --bootstrap-address is required for "
                             "admin network reconfiguration request.")
                raise exceptions.DCManagerClientException(error_msg)

            # Prompt the user for the subcloud's password if it isn't provided
            if parsed_args.sysadmin_password is not None:
                data['sysadmin_password'] = base64.b64encode(
                    parsed_args.sysadmin_password.encode("utf-8"))
            else:
                password = utils.prompt_for_password()
                data["sysadmin_password"] = base64.b64encode(
                    password.encode("utf-8"))

        if parsed_args.install_values:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = "install-values does not exist: %s" % \
                            parsed_args.install_values
                raise exceptions.DCManagerClientException(error_msg)
            files['install_values'] = parsed_args.install_values

            if parsed_args.bmc_password is not None:
                data['bmc_password'] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8"))
            else:
                password = utils.prompt_for_password('bmc')
                data["bmc_password"] = base64.b64encode(
                    password.encode("utf-8"))

        if not data:
            error_msg = "Nothing to update"
            raise exceptions.DCManagerClientException(error_msg)

        try:
            return dcmanager_client.subcloud_manager.update_subcloud(
                subcloud_ref, files=files, data=data)
        except Exception as e:
            print(e)
            error_msg = "Unable to update subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class ReconfigSubcloud(base.DCManagerShowOne):
    """Reconfigure a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(ReconfigSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to update.'
        )

        parser.add_argument(
            '--deploy-config',
            required=True,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be configured, '
                 'if not provided you will be prompted.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        files = dict()
        data = dict()

        # Get the deploy config yaml file
        if parsed_args.deploy_config is not None:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = "deploy-config file does not exist: %s" % \
                            parsed_args.deploy_config
                raise exceptions.DCManagerClientException(error_msg)
            files['deploy_config'] = parsed_args.deploy_config

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.sysadmin_password is not None:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8"))
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8"))

        try:
            return dcmanager_client.subcloud_manager.reconfigure_subcloud(
                subcloud_ref=subcloud_ref, files=files, data=data)
        except Exception as e:
            print(e)
            error_msg = "Unable to reconfigure subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class ReinstallSubcloud(base.DCManagerShowOne):
    """Reinstall a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(ReinstallSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to reinstall.'
        )

        parser.add_argument(
            '--bootstrap-values',
            required=True,
            help='YAML file containing subcloud configuration settings. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--deploy-config',
            required=False,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be configured, '
                 'if not provided you will be prompted.'
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        files = dict()
        data = dict()

        # Get the bootstrap values yaml file
        if not os.path.isfile(parsed_args.bootstrap_values):
            error_msg = "bootstrap-values does not exist: %s" % \
                        parsed_args.bootstrap_values
            raise exceptions.DCManagerClientException(error_msg)
        files['bootstrap_values'] = parsed_args.bootstrap_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config is not None:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = "deploy-config does not exist: %s" % \
                            parsed_args.deploy_config
                raise exceptions.DCManagerClientException(error_msg)
            files['deploy_config'] = parsed_args.deploy_config

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.sysadmin_password is not None:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8"))
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8"))

        # Require user to type reinstall to confirm
        print("WARNING: This will reinstall the subcloud. "
              "All applications and data on the subcloud will be lost.")
        confirm = six.moves.input(
            "Please type \"reinstall\" to confirm:").strip().lower()
        if confirm == 'reinstall':
            try:
                return dcmanager_client.subcloud_manager.reinstall_subcloud(
                    subcloud_ref=subcloud_ref, files=files, data=data)
            except Exception as e:
                print(e)
                error_msg = "Unable to reinstall subcloud %s" % (subcloud_ref)
                raise exceptions.DCManagerClientException(error_msg)
        else:
            msg = "Subcloud %s will not be reinstalled" % (subcloud_ref)
            raise exceptions.DCManagerClientException(msg)


class RestoreSubcloud(base.DCManagerShowOne):
    """Restore a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(RestoreSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            '--restore-values',
            required=False,
            help='YAML file containing subcloud restore settings. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be restored, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            '--with-install',
            required=False,
            action='store_true',
            help='option to reinstall the subcloud as part of restore, '
                 'suitable only for subclouds that can be installed remotely.'
        )

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to update.'
        )

        return parser

    def _get_resources(self, parsed_args):
        deprecation_msg = ('This command has been deprecated. Please use '
                           'subcloud-backup restore instead.')
        raise exceptions.DCManagerClientException(deprecation_msg)


class PrestageSubcloud(base.DCManagerShowOne):
    """Prestage a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(PrestageSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be prestaged, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to prestage.'
        )

        parser.add_argument(
            '--force',
            required=False,
            action='store_true',
            help='Disregard subcloud management alarm condition'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager
        data = dict()

        if parsed_args.force:
            data['force'] = 'true'

        if parsed_args.sysadmin_password is not None:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")).decode("utf-8")

        try:
            return dcmanager_client.subcloud_manager.\
                prestage_subcloud(
                    subcloud_ref=subcloud_ref, data=data)

        except Exception as e:
            print(e)
            error_msg = "Unable to prestage subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)
