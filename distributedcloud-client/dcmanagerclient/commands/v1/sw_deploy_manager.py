#
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import sw_update_manager

RELEASE_FIELD = -3


class SwDeployManagerMixin(object):
    """This Mixin provides the manager used for software deploy releases."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.sw_deploy_manager
        return dcmanager_client.sw_deploy_manager

    def custom_format_function(self, sw_update_strategy=None):
        original_fmt_func = super()._get_format_function()
        columns, data = original_fmt_func(sw_update_strategy)
        release_id = ""
        if sw_update_strategy and sw_update_strategy.extra_args:
            release_id = sw_update_strategy.extra_args.get("release_id")

        # Insert the 'release_id' field before the 'state',
        # 'created_at' and 'updated_at' fields
        columns = columns[:RELEASE_FIELD] + (
            "release_id",) + columns[RELEASE_FIELD:]
        data = data[:RELEASE_FIELD] + (release_id,) + data[RELEASE_FIELD:]
        return columns, data

    def _get_format_function(self):
        return self.custom_format_function


class CreateSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.CreateSwUpdateStrategy
):
    """Create a software deploy strategy."""

    def add_force_argument(self, parser):
        parser.add_argument(
            "--force",
            required=False,
            action="store_true",
            help="Skip checking the subcloud for management affecting alarms.",
        )

    def get_parser(self, prog_name):
        parser = super(CreateSwDeployStrategy, self).get_parser(prog_name)

        parser.add_argument(
            "--release-id",
            required=True,
            help="The release to be deployed.",
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for patching"""
        kwargs_dict["release_id"] = parsed_args.release_id

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        pass


class ShowSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.ShowSwUpdateStrategy
):
    """Show the details of a software deploy strategy for a subcloud."""
    pass


class DeleteSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.DeleteSwUpdateStrategy
):
    """Delete software deploy strategy from the database."""
    pass


class ApplySwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.ApplySwUpdateStrategy
):
    """Apply a software deploy strategy."""
    pass


class AbortSwDeployStrategy(
    SwDeployManagerMixin, sw_update_manager.AbortSwUpdateStrategy
):
    """Abort a software deploy strategy."""
    pass
