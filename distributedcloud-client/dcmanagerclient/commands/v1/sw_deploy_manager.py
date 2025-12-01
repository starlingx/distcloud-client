#
# Copyright (c) 2024-2025 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64

from dcmanagerclient.commands.v1 import sw_update_manager
from dcmanagerclient import exceptions
from dcmanagerclient import utils


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
        with_prestage = None
        if sw_update_strategy and sw_update_strategy.extra_args:
            release_id = sw_update_strategy.extra_args.get("release_id")
            snapshot = sw_update_strategy.extra_args.get("snapshot")
            rollback = sw_update_strategy.extra_args.get("rollback")
            if sw_update_strategy.extra_args.get("with_prestage"):
                with_prestage = "with_prestage"
            if sw_update_strategy.extra_args.get("with_delete"):
                delete_option = "with_delete"
            elif sw_update_strategy.extra_args.get("delete_only"):
                delete_option = "delete_only"

        extra_columns = (
            "release_id",
            "snapshot",
            "rollback",
            "delete_option",
            "with_prestage",
        )
        extra_data = (release_id, snapshot, rollback, delete_option, with_prestage)

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

    RELEASE_ID_ERROR_MSG = "The --release-id is required to create a deploy strategy."
    WITH_PRESTAGE_ERROR_MSG = (
        "--sysadmin-password can only be used with --with-prestage"
    )

    SNAPSHOT_ERROR_MSG = (
        "Option --snapshot cannot be used with any of the following options: "
        "--rollback or --delete-only."
    )

    WITH_DELETE_ERROR_MSG = (
        "Option --with-delete cannot be used with any of the following options: "
        "--rollback or --delete-only."
    )

    ROLLBACK_ERROR_MSG = (
        "Option --rollback cannot be used with any of the following options: "
        "--release-id, --delete-only or --with-prestage."
    )

    DELETE_ONLY_ERROR_MSG = (
        "Option --delete-only cannot be used with any of the following options: "
        "--release-id or --with-prestage."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "--release-id",
            required=False,
            help="The release ID to be deployed.",
        )

        self.add_argument(
            "--snapshot",
            required=False,
            action="store_true",
            help="Create snapshot before update (default: False).",
        )

        self.add_argument(
            "--rollback",
            required=False,
            action="store_true",
            help="Performs a rollback of the active software deployment",
        )

        self.add_argument(
            "--with-delete",
            required=False,
            action="store_true",
            help="Deletes the software deployment after the strategy apply",
        )

        self.add_argument(
            "--delete-only",
            required=False,
            action="store_true",
            help=(
                "Deletes the software deployment without "
                "applying the subcloud strategy"
            ),
        )

        self.add_argument(
            "--sysadmin-password",
            required=False,
            help=(
                "Sysadmin password of the subcloud. If not provided, you will be "
                "prompted. This parameter is only required if --with-prestage is used."
            ),
        )

        self.add_argument(
            "--with-prestage",
            required=False,
            action="store_true",
            help=(
                "Prestage the subcloud, if not already prestaged, before applying "
                "the strategy."
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
        with_prestage = parsed_args.with_prestage
        sysadmin_password = parsed_args.sysadmin_password

        if sysadmin_password and not with_prestage:
            raise exceptions.DCManagerClientException(self.WITH_PRESTAGE_ERROR_MSG)

        if not release_id and not (rollback or delete_only):
            raise exceptions.DCManagerClientException(self.RELEASE_ID_ERROR_MSG)

        if snapshot and (rollback or delete_only):
            raise exceptions.DCManagerClientException(self.SNAPSHOT_ERROR_MSG)

        if with_delete and (rollback or delete_only):
            raise exceptions.DCManagerClientException(self.WITH_DELETE_ERROR_MSG)

        if rollback and (release_id or delete_only or with_prestage):
            raise exceptions.DCManagerClientException(self.ROLLBACK_ERROR_MSG)

        if delete_only and (release_id or with_prestage):
            raise exceptions.DCManagerClientException(self.DELETE_ONLY_ERROR_MSG)

        if release_id:
            kwargs_dict["release_id"] = release_id

        if with_prestage:
            # Prompt the user for the subcloud's password if it isn't provided
            if sysadmin_password is not None:
                # The binary base64 encoded string (eg. b'dGVzdA==') is not JSON
                # serializable in Python3.x, so it has to be decoded to a JSON
                # serializable string (eg. 'dGVzdA==').
                kwargs_dict["sysadmin_password"] = base64.b64encode(
                    sysadmin_password.encode("utf-8")
                ).decode("utf-8")
            else:
                password = utils.prompt_for_password()
                kwargs_dict["sysadmin_password"] = base64.b64encode(
                    password.encode("utf-8")
                ).decode("utf-8")

        kwargs_dict["snapshot"] = snapshot
        kwargs_dict["rollback"] = rollback
        kwargs_dict["with_delete"] = with_delete
        kwargs_dict["delete_only"] = delete_only
        kwargs_dict["with_prestage"] = with_prestage


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
