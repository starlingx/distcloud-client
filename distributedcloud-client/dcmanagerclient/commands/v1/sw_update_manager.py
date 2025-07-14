# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2020-2025 Wind River Systems, Inc.
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

from dcmanagerclient import exceptions
from dcmanagerclient.commands.v1 import base


# These are the abstract base classes used for sw update managers such as
# fw-update-manager
#
# also handles 'steps' and 'strategies'


def detail_format(sw_update_strategy=None):
    columns = (
        "strategy type",
        "subcloud apply type",
        "max parallel subclouds",
        "stop on failure",
        "state",
        "created_at",
        "updated_at",
    )

    if sw_update_strategy:
        data = (
            sw_update_strategy.strategy_type,
            sw_update_strategy.subcloud_apply_type,
            sw_update_strategy.max_parallel_subclouds,
            sw_update_strategy.stop_on_failure,
            sw_update_strategy.state,
            sw_update_strategy.created_at,
            sw_update_strategy.updated_at,
        )
    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def strategy_step_format(strategy_step=None):
    columns = ("cloud", "stage", "state", "details", "started_at", "finished_at")

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
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def detail_strategy_step_format(strategy_step=None):
    columns = (
        "cloud",
        "stage",
        "state",
        "details",
        "started_at",
        "finished_at",
        "created_at",
        "updated_at",
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
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


class CreateSwUpdateStrategy(base.DCManagerShowOne):
    """Create a software update strategy."""

    def get_sw_update_manager(self):
        # This method must be overrridden by the concrete subclass
        raise NotImplementedError

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--subcloud-apply-type",
            required=False,
            choices=["parallel", "serial"],
            help="Subcloud apply type (parallel or serial).",
        )

        parser.add_argument(
            "--max-parallel-subclouds",
            required=False,
            type=int,
            help="Maximum number of parallel subclouds.",
        )

        parser.add_argument(
            "--stop-on-failure",
            required=False,
            action="store_true",
            help="Do not update any additional subclouds after a failure.",
        )

        parser.add_argument(
            "--group", required=False, help="Name or ID of subcloud group to update."
        )

        parser.add_argument(
            "cloud_name",
            nargs="?",
            default=None,
            help="Name of a single cloud to update.",
        )

        return parser

    def validate_group_params(self, parsed_args):
        """When specifying a group, other inputs are considered invalid"""
        if parsed_args.group:
            if parsed_args.cloud_name:
                error_msg = "The cloud_name and group options are mutually exclusive."
                raise exceptions.DCManagerClientException(error_msg)
            if parsed_args.subcloud_apply_type:
                error_msg = (
                    "The --subcloud-apply-type is not "
                    "supported when --group option is applied."
                )
                raise exceptions.DCManagerClientException(error_msg)
            if parsed_args.max_parallel_subclouds:
                error_msg = (
                    "The --max-parallel-subclouds options is not "
                    "supported when --group option is applied."
                )
                raise exceptions.DCManagerClientException(error_msg)

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args based on the subclass"""

    def _get_resources(self, parsed_args):
        kwargs = {}
        if parsed_args.subcloud_apply_type:
            kwargs["subcloud-apply-type"] = parsed_args.subcloud_apply_type
        if parsed_args.max_parallel_subclouds:
            kwargs["max-parallel-subclouds"] = parsed_args.max_parallel_subclouds
        if parsed_args.stop_on_failure:
            kwargs["stop-on-failure"] = "true"
        if parsed_args.cloud_name is not None:
            kwargs["cloud_name"] = parsed_args.cloud_name
        if parsed_args.group is not None:
            kwargs["subcloud_group"] = parsed_args.group

        self.validate_group_params(parsed_args)

        # Add more kwargs based on the update type
        self.process_custom_params(parsed_args, kwargs)

        return self.get_sw_update_manager().create_sw_update_strategy(**kwargs)


class ShowSwUpdateStrategy(base.DCManagerShowOne):
    """Show the details of an software update strategy for a subcloud."""

    def get_sw_update_manager(self):
        # This method must be overrridden by the concrete subclass
        raise NotImplementedError

    def _get_format_function(self):
        return detail_format

    def _get_resources(self, parsed_args):
        return self.get_sw_update_manager().update_sw_strategy_detail()


class DeleteSwUpdateStrategy(base.DCManagerShowOne):
    """Delete a software update strategy from the database."""

    requires_confirmation = True

    def get_sw_update_manager(self):
        # This method must be overrridden by the concrete subclass
        raise NotImplementedError

    def _get_format_function(self):
        return detail_format

    def _get_resources(self, parsed_args):
        return self.get_sw_update_manager().delete_sw_update_strategy()

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser


class ApplySwUpdateStrategy(base.DCManagerShowOne):
    """Apply a software update strategy."""

    requires_confirmation = True

    def get_sw_update_manager(self):
        # This method must be overrridden by the concrete subclass
        raise NotImplementedError

    def _get_format_function(self):
        return detail_format

    def _get_resources(self, parsed_args):
        return self.get_sw_update_manager().apply_sw_update_strategy()


class AbortSwUpdateStrategy(base.DCManagerShowOne):
    """Abort a software update strategy."""

    def get_sw_update_manager(self):
        # This method must be overrridden by the concrete subclass
        raise NotImplementedError

    def _get_format_function(self):
        return detail_format

    def _get_resources(self, parsed_args):
        return self.get_sw_update_manager().abort_sw_update_strategy()


class ListSwUpdateStrategyStep(base.DCManagerLister):
    """List strategy steps."""

    def get_strategy_step_manager(self):
        strategy_step_manager = self.app.client_manager.strategy_step_manager
        return strategy_step_manager

    def _get_format_function(self):
        return strategy_step_format

    def _get_resources(self, parsed_args):
        return self.get_strategy_step_manager().list_strategy_steps()


class ShowSwUpdateStrategyStep(base.DCManagerShowOne):
    """Show the details of a strategy step."""

    def get_strategy_step_manager(self):
        strategy_step_manager = self.app.client_manager.strategy_step_manager
        return strategy_step_manager

    def _get_format_function(self):
        return detail_strategy_step_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("cloud_name", help="Name of cloud to view the details.")
        return parser

    def _get_resources(self, parsed_args):
        cloud_name = parsed_args.cloud_name
        return self.get_strategy_step_manager().strategy_step_detail(cloud_name)
