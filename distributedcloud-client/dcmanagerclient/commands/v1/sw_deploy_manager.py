#
# Copyright (c) 2024-2025 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import sw_update_manager


class SwDeployManagerMixin:
    """This Mixin provides the manager used for software deploy releases."""

    def get_sw_update_manager(self):
        sw_deploy_manager = self.app.client_manager.sw_deploy_manager
        return sw_deploy_manager

    def custom_format_function(self, sw_update_strategy=None):
        original_fmt_func = super()._get_format_function()
        columns, data = original_fmt_func(sw_update_strategy)
        release_id = ""
        snapshot = False
        if sw_update_strategy and sw_update_strategy.extra_args:
            release_id = sw_update_strategy.extra_args.get("release_id")
            snapshot = sw_update_strategy.extra_args.get("snapshot")

        # Find the index of 'stop on failure' in the tuple
        failure_status_index = columns.index("stop on failure")

        # Insert the 'release_id' field after the 'stop on failure',
        columns = (
            columns[: failure_status_index + 1]
            + ("release_id", "snapshot")
            + columns[failure_status_index + 1 :]
        )
        data = (
            data[: failure_status_index + 1]
            + (release_id, snapshot)
            + data[failure_status_index + 1 :]
        )
        return columns, data

    def _get_format_function(self):
        return self.custom_format_function


class CreateSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.CreateSwUpdateStrategy
):
    """Create a software deploy strategy."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "release_id",
            help="The release ID to be deployed.",
        )

        parser.add_argument(
            "--snapshot",
            required=False,
            action="store_true",
            help="Create snapshot before update (default: False).",
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for patching"""
        kwargs_dict["release_id"] = parsed_args.release_id
        kwargs_dict["snapshot"] = parsed_args.snapshot


class ShowSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.ShowSwUpdateStrategy
):
    """Show the details of a software deploy strategy for a subcloud."""


class DeleteSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.DeleteSwUpdateStrategy
):
    """Delete software deploy strategy from the database."""


class ApplySwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.ApplySwUpdateStrategy
):
    """Apply a software deploy strategy."""


class AbortSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.AbortSwUpdateStrategy
):
    """Abort a software deploy strategy."""
