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

DEFAULT_REGION_NAME = "RegionOne"


def options_detail_format(sw_update_options=None):

    columns = (
        'cloud',
        'storage apply type',
        'compute apply type',
        'max parallel computes',
        'alarm restriction type',
        'default instance action',
        'created_at',
        'updated_at',
    )

    if sw_update_options:
        data = (
            sw_update_options.cloud,
            sw_update_options.storage_apply_type,
            sw_update_options.compute_apply_type,
            sw_update_options.max_parallel_computes,
            sw_update_options.alarm_restriction_type,
            sw_update_options.default_instance_action,
            sw_update_options.created_at,
            sw_update_options.updated_at,
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def options_list_format(sw_update_option=None):
    columns = (
        'cloud',
        'storage apply type',
        'compute apply type',
        'max parallel computes',
        'alarm restriction type',
        'default instance action',
    )

    if sw_update_option:
        data = (
            sw_update_option.cloud,
            sw_update_option.storage_apply_type,
            sw_update_option.compute_apply_type,
            sw_update_option.max_parallel_computes,
            sw_update_option.alarm_restriction_type,
            sw_update_option.default_instance_action,
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class UpdateSwUpdateOptions(base.DCManagerShowOne):
    """Update patch options, defaults or per subcloud."""

    def _get_format_function(self):
        return options_detail_format

    def get_parser(self, parsed_args):
        parser = super(UpdateSwUpdateOptions, self).get_parser(parsed_args)

        parser.add_argument(
            '--storage-apply-type',
            required=True,
            choices=['parallel', 'serial'],
            help='Storage node apply type (parallel or serial).'
        )

        parser.add_argument(
            '--compute-apply-type',
            required=True,
            choices=['parallel', 'serial'],
            help='Compute node apply type (parallel or serial).'
        )

        parser.add_argument(
            '--max-parallel-computes',
            required=True,
            type=int,
            help='Maximum number of parallel computes.'
        )

        parser.add_argument(
            '--alarm-restriction-type',
            required=True,
            choices=['strict', 'relaxed'],
            help='Whether to allow patching if subcloud alarms are present or '
                 'not (strict, relaxed).'
        )

        parser.add_argument(
            '--default-instance-action',
            required=True,
            choices=['stop-start', 'migrate'],
            help='How instances should be handled.'
        )

        parser.add_argument(
            'subcloud',
            nargs='?',
            default=None,
            help='Subcloud name or id, omit to set default options.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.sw_update_options_manager
        kwargs = dict()
        kwargs['storage-apply-type'] = parsed_args.storage_apply_type
        kwargs['compute-apply-type'] = parsed_args.compute_apply_type
        kwargs['max-parallel-computes'] = parsed_args.max_parallel_computes
        kwargs['alarm-restriction-type'] = parsed_args.alarm_restriction_type
        kwargs['default-instance-action'] = parsed_args.default_instance_action

        try:
            return dcmanager_client.sw_update_options_manager.\
                sw_update_options_update(subcloud_ref, **kwargs)
        except Exception as e:
            print (e)
            error_msg = "Unable to update patch options for subcloud %s" % \
                (subcloud_ref)
            raise exceptions.DCManagerClientException(error_msg)


class ListSwUpdateOptions(base.DCManagerLister):
    """List patch options."""

    def _get_format_function(self):
        return options_list_format

    def get_parser(self, parsed_args):
        parser = super(ListSwUpdateOptions, self).get_parser(parsed_args)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.sw_update_options_manager
        return dcmanager_client.sw_update_options_manager.\
            sw_update_options_list()


class ShowSwUpdateOptions(base.DCManagerShowOne):
    """Show patch options, defaults or per subcloud."""

    def _get_format_function(self):
        return options_detail_format

    def get_parser(self, parsed_args):
        parser = super(ShowSwUpdateOptions, self).get_parser(parsed_args)

        parser.add_argument(
            'subcloud',
            nargs='?',
            default=None,
            help='Subcloud name or id, omit to show default options.'
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.sw_update_options_manager
        return dcmanager_client.sw_update_options_manager.\
            sw_update_options_detail(subcloud_ref)


class DeleteSwUpdateOptions(command.Command):
    """Delete per subcloud patch options."""

    def get_parser(self, prog_name):
        parser = super(DeleteSwUpdateOptions, self).get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Subcloud name or id'
        )

        return parser

    def take_action(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        dcmanager_client = self.app.client_manager.sw_update_options_manager
        try:
            return dcmanager_client.sw_update_options_manager.\
                sw_update_options_delete(subcloud_ref)
        except Exception as e:
            print (e)
            error_msg = "Unable to delete patch options"
            raise exceptions.DCManagerClientException(error_msg)
