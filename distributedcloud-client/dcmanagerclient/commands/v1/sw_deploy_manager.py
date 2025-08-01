#
# Copyright (c) 2024-2025 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import sw_update_manager
from dcmanagerclient import exceptions


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
        rollback = False
        delete_option = None
        if sw_update_strategy and sw_update_strategy.extra_args:
            release_id = sw_update_strategy.extra_args.get("release_id")
            snapshot = sw_update_strategy.extra_args.get("snapshot")
            rollback = sw_update_strategy.extra_args.get("rollback")
            if sw_update_strategy.extra_args.get("with_delete"):
                delete_option = "with_delete"
            elif sw_update_strategy.extra_args.get("delete_only"):
                delete_option = "delete_only"

        extra_columns = ("release_id", "snapshot", "rollback", "delete_option")
        extra_data = (release_id, snapshot, rollback, delete_option)

        # Find the index of 'stop on failure' in the tuple
        failure_status_index = columns.index("stop on failure")

        # Insert the extra_args fields after the 'stop on failure',
        columns = (
            columns[: failure_status_index + 1]
            + extra_columns
            + columns[failure_status_index + 1 :]
        )
        data = (
            data[: failure_status_index + 1]
            + extra_data
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
            nargs="?",
            help="The release ID to be deployed.",
        )

        parser.add_argument(
            "--snapshot",
            required=False,
            action="store_true",
            help="Create snapshot before update (default: False).",
        )

        parser.add_argument(
            "--rollback",
            required=False,
            action="store_true",
            help="Performs a rollback of the active software deployment",
        )

        parser.add_argument(
            "--with-delete",
            required=False,
            action="store_true",
            help="Deletes the software deployment after the strategy apply",
        )

        parser.add_argument(
            "--delete-only",
            required=False,
            action="store_true",
            help=(
                "Deletes the software deployment without "
                "applying the subcloud strategy"
            ),
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for patching"""
        release_id = parsed_args.release_id
        snapshot = parsed_args.snapshot
        rollback = parsed_args.rollback
        with_delete = parsed_args.with_delete
        delete_only = parsed_args.delete_only

        if not release_id and not (rollback or delete_only):
            error_msg = "The release_id is required to create a deploy strategy."
            raise exceptions.DCManagerClientException(error_msg)

        if snapshot and (rollback or delete_only):
            error_msg = (
                "Option --snapshot cannot be used with any of the following "
                "options: --rollback or --delete-only."
            )
            raise exceptions.DCManagerClientException(error_msg)

        if rollback and (release_id or snapshot or with_delete or delete_only):
            error_msg = (
                "Option --rollback cannot be used with any of the following "
                "options: release-id, --snapshot, --with-delete or --delete-only."
            )
            raise exceptions.DCManagerClientException(error_msg)

        if with_delete and (rollback or delete_only):
            error_msg = (
                "Option --with-delete cannot be used with any of the following "
                "options: --rollback or --delete-only."
            )
            raise exceptions.DCManagerClientException(error_msg)

        if delete_only and (release_id or snapshot or rollback or with_delete):
            error_msg = (
                "Option --delete-only cannot be used with any of the following "
                "options: release-id, --snapshot, --rollback or --with-delete."
            )
            raise exceptions.DCManagerClientException(error_msg)

        kwargs_dict["release_id"] = release_id
        kwargs_dict["snapshot"] = snapshot
        kwargs_dict["rollback"] = rollback
        kwargs_dict["with_delete"] = with_delete
        kwargs_dict["delete_only"] = delete_only


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
