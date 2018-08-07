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

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions


def detail_format(sw_update_strategy=None):
    columns = (
        'subcloud apply type',
        'max parallel subclouds',
        'stop on failure',
        'state',
        'created_at',
        'updated_at',
    )

    if sw_update_strategy:
        data = (
            sw_update_strategy.subcloud_apply_type,
            sw_update_strategy.max_parallel_subclouds,
            sw_update_strategy.stop_on_failure,
            sw_update_strategy.state,
            sw_update_strategy.created_at,
            sw_update_strategy.updated_at,
        )
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def strategy_step_format(strategy_step=None):
    columns = (
        'cloud',
        'stage',
        'state',
        'details',
        'started_at',
        'finished_at',
    )

    if strategy_step:
        data = (
            strategy_step.cloud,
            strategy_step.stage,
            strategy_step.state,
            strategy_step.details,
            strategy_step.started_at,
            strategy_step.finished_at,
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


def detail_strategy_step_format(strategy_step=None):
    columns = (
        'cloud',
        'stage',
        'state',
        'details',
        'started_at',
        'finished_at',
        'created_at',
        'updated_at',
    )

    if strategy_step:
        data = (
            strategy_step.cloud,
            strategy_step.stage,
            strategy_step.state,
            strategy_step.details,
            strategy_step.started_at,
            strategy_step.finished_at,
            strategy_step.created_at,
            strategy_step.updated_at,
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class CreatePatchStrategy(base.DCManagerShowOne):
    """Create a patch strategy."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, parsed_args):
        parser = super(CreatePatchStrategy, self).get_parser(parsed_args)

        parser.add_argument(
            '--subcloud-apply-type',
            required=False,
            choices=['parallel', 'serial'],
            help='Subcloud apply type (parallel or serial).'
        )

        parser.add_argument(
            '--max-parallel-subclouds',
            required=False,
            type=int,
            help='Maximum number of parallel subclouds.'
        )

        parser.add_argument(
            '--stop-on-failure',
            required=False,
            action='store_true',
            help='Do not patch any additional subclouds after a failure.'
        )

        parser.add_argument(
            'cloud_name',
            nargs='?',
            default=None,
            help='Name of a single cloud to patch.'
        )

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.sw_update_manager
        kwargs = dict()
        if parsed_args.subcloud_apply_type:
            kwargs['subcloud-apply-type'] = parsed_args.subcloud_apply_type
        if parsed_args.max_parallel_subclouds:
            kwargs['max-parallel-subclouds'] = \
                parsed_args.max_parallel_subclouds
        if parsed_args.stop_on_failure:
            kwargs['stop-on-failure'] = 'true'
        if parsed_args.cloud_name is not None:
            kwargs['cloud_name'] = parsed_args.cloud_name
        return dcmanager_client.sw_update_manager.create_patch_strategy(
            **kwargs)


class ShowPatchStrategy(base.DCManagerShowOne):
    """Show the details of a patch strategy for a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, parsed_args):
        parser = super(ShowPatchStrategy, self).get_parser(parsed_args)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.sw_update_manager
        return dcmanager_client.sw_update_manager.patch_strategy_detail()


class DeletePatchStrategy(base.DCManagerShowOne):
    """Delete patch strategy from the database."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(DeletePatchStrategy, self).get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.sw_update_manager
        try:
            return dcmanager_client.sw_update_manager.delete_patch_strategy()
        except Exception as e:
            print (e)
            error_msg = "Unable to delete patch strategy"
            raise exceptions.DCManagerClientException(error_msg)


class ApplyPatchStrategy(base.DCManagerShowOne):
    """Apply a patch strategy."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(ApplyPatchStrategy, self).get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.sw_update_manager
        try:
            return dcmanager_client.sw_update_manager.apply_patch_strategy()
        except Exception as e:
            print (e)
            error_msg = "Unable to apply patch strategy"
            raise exceptions.DCManagerClientException(error_msg)


class AbortPatchStrategy(base.DCManagerShowOne):
    """Abort a patch strategy."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(AbortPatchStrategy, self).get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.sw_update_manager
        try:
            return dcmanager_client.sw_update_manager.abort_patch_strategy()
        except Exception as e:
            print (e)
            error_msg = "Unable to abort patch strategy"
            raise exceptions.DCManagerClientException(error_msg)


class ListStrategyStep(base.DCManagerLister):
    """List strategy steps."""

    def _get_format_function(self):
        return strategy_step_format

    def get_parser(self, parsed_args):
        parser = super(ListStrategyStep, self).get_parser(parsed_args)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.strategy_step_manager
        return dcmanager_client.strategy_step_manager.list_strategy_steps()


class ShowStrategyStep(base.DCManagerShowOne):
    """Show the details of a strategy step."""

    def _get_format_function(self):
        return detail_strategy_step_format

    def get_parser(self, parsed_args):
        parser = super(ShowStrategyStep, self).get_parser(parsed_args)

        parser.add_argument(
            'cloud_name',
            help='Name of cloud to view the details.'
        )

        return parser

    def _get_resources(self, parsed_args):
        cloud_name = parsed_args.cloud_name
        dcmanager_client = self.app.client_manager.strategy_step_manager
        return dcmanager_client.strategy_step_manager.strategy_step_detail(
            cloud_name)
