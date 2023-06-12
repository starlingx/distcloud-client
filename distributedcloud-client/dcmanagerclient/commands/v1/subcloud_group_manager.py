# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2020-2021 Wind River Systems, Inc.
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

from osc_lib.command import command

from dcmanagerclient.commands.v1 import base
from dcmanagerclient.commands.v1.subcloud_manager import detail_format
from dcmanagerclient.commands.v1.subcloud_manager \
    import update_fields_values
from dcmanagerclient import exceptions


def group_format(subcloud_group=None):
    columns = (
        'id',
        'name',
        'description',
    )

    if subcloud_group:
        data = (
            subcloud_group.group_id,
            subcloud_group.name,
            subcloud_group.description,
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def detail_group_format(subcloud_group=None):
    # Include all the fields in group_format
    # plus some additional fields
    columns = (
        'id',
        'name',
        'description',
        'update apply type',
        'max parallel subclouds',
        'created_at',
        'updated_at',
    )

    if subcloud_group:
        data = (
            subcloud_group.group_id,
            subcloud_group.name,
            subcloud_group.description,
            subcloud_group.update_apply_type,
            subcloud_group.max_parallel_subclouds,
            subcloud_group.created_at,
            subcloud_group.updated_at,
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class AddSubcloudGroup(base.DCManagerShowOne):
    """Add a new subcloud group."""

    def _get_format_function(self):
        return detail_group_format

    def get_parser(self, prog_name):
        parser = super(AddSubcloudGroup, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            required=True,
            help='Name for the new subcloud group.'
        )

        parser.add_argument(
            '--description',
            required=False,
            default='No description provided',
            help='Description of new subcloud group.'
        )

        parser.add_argument(
            '--update_apply_type',
            required=False,
            default='parallel',
            help='apply type for the new subcloud group.'
        )

        parser.add_argument(
            '--max_parallel_subclouds',
            required=False,
            default=2,
            help='max parallel subclouds for the new subcloud group.'
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_group_manager
        kwargs = dict()

        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name

        if parsed_args.description is not None:
            kwargs['description'] = parsed_args.description

        if parsed_args.update_apply_type is not None:
            kwargs['update_apply_type'] = parsed_args.update_apply_type

        if parsed_args.max_parallel_subclouds is not None:
            kwargs['max_parallel_subclouds'] = \
                parsed_args.max_parallel_subclouds
        return dcmanager_client.subcloud_group_manager.add_subcloud_group(
            **kwargs)


class ListSubcloudGroup(base.DCManagerLister):
    """List subcloud groups."""

    def _get_format_function(self):
        return group_format

    def get_parser(self, prog_name):
        parser = super(ListSubcloudGroup, self).get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_group_manager
        return dcmanager_client.subcloud_group_manager.list_subcloud_groups()


class ListSubcloudGroupSubclouds(base.DCManagerLister):
    """List subclouds referencing a subcloud group."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(ListSubcloudGroupSubclouds, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            help='Name or ID of subcloud group to list associated subclouds.'
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_group_ref = parsed_args.group
        dcmanager_client = self.app.client_manager.subcloud_group_manager
        result = dcmanager_client.subcloud_group_manager. \
            subcloud_group_list_subclouds(subcloud_group_ref)
        update_fields_values(result)
        return result


class ShowSubcloudGroup(base.DCManagerShowOne):
    """Show the details of a subcloud group."""

    def _get_format_function(self):
        return detail_group_format

    def get_parser(self, prog_name):
        parser = super(ShowSubcloudGroup, self).get_parser(prog_name)

        parser.add_argument(
            'group',
            help='Name or ID of subcloud group to view the details.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_group_ref = parsed_args.group
        dcmanager_client = self.app.client_manager.subcloud_group_manager
        return dcmanager_client.subcloud_group_manager.\
            subcloud_group_detail(subcloud_group_ref)


class DeleteSubcloudGroup(command.Command):
    """Delete subcloud group details from the database."""

    def get_parser(self, prog_name):
        parser = super(DeleteSubcloudGroup, self).get_parser(prog_name)

        parser.add_argument(
            'group',
            help='Name or ID of the subcloud group to delete.'
        )
        return parser

    def take_action(self, parsed_args):
        subcloud_group_ref = parsed_args.group
        dcmanager_client = self.app.client_manager.subcloud_group_manager
        try:
            dcmanager_client.subcloud_group_manager.\
                delete_subcloud_group(subcloud_group_ref)
        except Exception as e:
            print(e)
            msg = "Unable to delete subcloud group %s" % (subcloud_group_ref)
            raise exceptions.DCManagerClientException(msg)


class UpdateSubcloudGroup(base.DCManagerShowOne):
    """Update attributes of a subcloud group."""

    def _get_format_function(self):
        return detail_group_format

    def get_parser(self, prog_name):
        parser = super(UpdateSubcloudGroup, self).get_parser(prog_name)

        parser.add_argument(
            'group',
            help='Name or ID of the subcloud group to update.'
        )

        parser.add_argument(
            '--name',
            required=False,
            help='Name of subcloud group.'
        )

        parser.add_argument(
            '--description',
            required=False,
            help='Description of subcloud group.'
        )

        parser.add_argument(
            '--update_apply_type',
            required=False,
            help='Update apply type of subcloud group.'
        )

        parser.add_argument(
            '--max_parallel_subclouds',
            type=int,
            required=False,
            help='max parallel subclouds of subcloud group.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_group_ref = parsed_args.group
        dcmanager_client = self.app.client_manager.subcloud_group_manager
        kwargs = dict()
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.update_apply_type:
            kwargs['update_apply_type'] = parsed_args.update_apply_type
        if parsed_args.max_parallel_subclouds:
            kwargs['max_parallel_subclouds'] = \
                parsed_args.max_parallel_subclouds
        if len(kwargs) == 0:
            error_msg = "Nothing to update"
            raise exceptions.DCManagerClientException(error_msg)

        try:
            return dcmanager_client. \
                subcloud_group_manager.update_subcloud_group(
                    subcloud_group_ref, **kwargs)
        except Exception as e:
            print(e)
            msg = "Unable to update subcloud group %s" % (subcloud_group_ref)
            raise exceptions.DCManagerClientException(msg)
