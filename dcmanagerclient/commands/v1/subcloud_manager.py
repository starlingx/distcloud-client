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
# Copyright (c) 2017 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

from osc_lib.command import command

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions


def format(subcloud=None):
    columns = (
        'id',
        'name',
        'management',
        'availability',
        'sync'
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.management_state,
            subcloud.availability_status,
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
            '--name',
            required=True,
            help='Name of subcloud.'
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
            '--management-subnet',
            required=True,
            help='Management subnet for subcloud in CIDR format.'
        )

        parser.add_argument(
            '--management-start-ip',
            required=True,
            help='Start of management IP address range for subcloud'
        )

        parser.add_argument(
            '--management-end-ip',
            required=True,
            help='End of management IP address range for subcloud',
        )

        parser.add_argument(
            '--management-gateway-ip',
            required=True,
            help='Management gateway IP for subcloud',
        )

        parser.add_argument(
            '--systemcontroller-gateway-ip',
            required=True,
            help='Central gateway IP',
        )

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_manager
        kwargs = dict()
        kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.location:
            kwargs['location'] = parsed_args.location
        kwargs['management-subnet'] = parsed_args.management_subnet
        kwargs['management-start-ip'] = parsed_args.management_start_ip
        kwargs['management-end-ip'] = parsed_args.management_end_ip
        kwargs['management-gateway-ip'] = parsed_args.management_gateway_ip
        kwargs['systemcontroller-gateway-ip'] = \
            parsed_args.systemcontroller_gateway_ip
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
            print (e)
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
            print (e)
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
            print (e)
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
            print (e)
            error_msg = "Unable to update subcloud %s" % (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class GenerateConfigSubcloud(command.Command):
    """Generate configuration for a subcloud."""

    def get_parser(self, prog_name):
        parser = super(GenerateConfigSubcloud, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to generate config.'
        )

        parser.add_argument(
            '--pxe-subnet',
            required=False,
            help='PXE boot subnet for subcloud in CIDR format.'
        )

        parser.add_argument(
            '--management-vlan',
            required=False,
            help='VLAN for subcloud management network.'
        )

        parser.add_argument(
            '--management-interface-port',
            required=False,
            help='Subcloud management interface port.'
        )

        parser.add_argument(
            '--management-interface-mtu',
            required=False,
            help='Subcloud management interface mtu.'
        )

        parser.add_argument(
            '--oam-subnet',
            required=False,
            help='OAM subnet for subcloud in CIDR format.'
        )

        parser.add_argument(
            '--oam-gateway-ip',
            required=False,
            help='OAM gateway IP for subcloud.'
        )

        parser.add_argument(
            '--oam-floating-ip',
            required=False,
            help='OAM floating IP address for subcloud.'
        )

        parser.add_argument(
            '--oam-unit-0-ip',
            required=False,
            help='OAM unit 0 IP address for subcloud.'
        )

        parser.add_argument(
            '--oam-unit-1-ip',
            required=False,
            help='OAM unit 1 IP address for subcloud.'
        )

        parser.add_argument(
            '--oam-interface-port',
            required=False,
            help='Subcloud OAM interface port.'
        )

        parser.add_argument(
            '--oam-interface-mtu',
            required=False,
            help='Subcloud OAM interface mtu.'
        )

        parser.add_argument(
            '--system-mode',
            required=False,
            help='System mode',
            choices=['simplex', 'duplex', 'duplex-direct']
        )

        return parser

    def take_action(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.subcloud_manager

        kwargs = dict()
        if parsed_args.pxe_subnet:
            kwargs['pxe-subnet'] = \
                parsed_args.pxe_subnet
        if parsed_args.management_vlan:
            kwargs['management-vlan'] = \
                parsed_args.management_vlan
        if parsed_args.management_interface_port:
            kwargs['management-interface-port'] = \
                parsed_args.management_interface_port
        if parsed_args.management_interface_mtu:
            kwargs['management-interface-mtu'] = \
                parsed_args.management_interface_mtu
        if parsed_args.oam_subnet:
            kwargs['oam-subnet'] = parsed_args.oam_subnet
        if parsed_args.oam_gateway_ip:
            kwargs['oam-gateway-ip'] = parsed_args.oam_gateway_ip
        if parsed_args.oam_floating_ip:
            kwargs['oam-floating-ip'] = parsed_args.oam_floating_ip
        if parsed_args.oam_unit_0_ip:
            kwargs['oam-unit-0-ip'] = parsed_args.oam_unit_0_ip
        if parsed_args.oam_unit_1_ip:
            kwargs['oam-unit-1-ip'] = parsed_args.oam_unit_1_ip
        if parsed_args.oam_interface_port:
            kwargs['oam-interface-port'] = parsed_args.oam_interface_port
        if parsed_args.oam_interface_mtu:
            kwargs['oam-interface-mtu'] = parsed_args.oam_interface_mtu
        if parsed_args.system_mode:
            kwargs['system-mode'] = parsed_args.system_mode

        try:
            subcloud_config = dcmanager_client.subcloud_manager.\
                generate_config_subcloud(subcloud_ref, **kwargs)
            return subcloud_config

        except Exception as e:
            print (e)
            error_msg = "Unable to generate config for subcloud %s" % \
                        (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)
