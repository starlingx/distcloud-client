# Copyright (c) 2023-2025 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import base64

from osc_lib.command import command

from dcmanagerclient import exceptions
from dcmanagerclient import utils
from dcmanagerclient.commands.v1 import base
from dcmanagerclient.commands.v1.base import ConfirmationMixin


def group_format(subcloud_peer_group=None):
    columns = (
        "id",
        "peer_group_name",
        "group_priority",
        "group_state",
        "system_leader_id",
        "system_leader_name",
        "max_subcloud_rehoming",
        "created_at",
        "updated_at",
    )

    if subcloud_peer_group:
        data = (
            subcloud_peer_group.id,
            subcloud_peer_group.peer_group_name,
            subcloud_peer_group.group_priority,
            subcloud_peer_group.group_state,
            subcloud_peer_group.system_leader_id,
            subcloud_peer_group.system_leader_name,
            subcloud_peer_group.max_subcloud_rehoming,
            subcloud_peer_group.created_at,
            subcloud_peer_group.updated_at,
        )

    else:
        data = (("<none>",) * len(columns),)

    return columns, data


class MigrateSubcloudPeerGroup(base.DCManagerLister):
    """Migrate subclouds in this peer group."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "group", help="Name or ID of the subcloud peer group to migrate."
        )

        self.add_argument(
            "--sysadmin-password",
            required=False,
            help="Sysadmin password of the subclouds to be configured, "
            "if not provided you will be prompted.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_ref = parsed_args.group
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        kwargs = {}

        if parsed_args.sysadmin_password is not None:
            kwargs["sysadmin_password"] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")
            ).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            kwargs["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")
            ).decode("utf-8")

        try:
            return subcloud_peer_group_manager.migrate_subcloud_peer_group(
                subcloud_peer_group_ref, **kwargs
            )
        except Exception as exc:
            print(exc)
            msg = f"Unable to migrate subcloud peer group {subcloud_peer_group_ref}"
            raise exceptions.DCManagerClientException(msg)


class AddSubcloudPeerGroup(base.DCManagerShowOne):
    """Add a new subcloud peer group."""

    def _get_format_function(self):
        return group_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "--peer-group-name",
            required=True,
            help="Name for the new subcloud peer group.",
        )

        self.add_argument(
            "--group-state",
            required=False,
            choices=["enabled", "disabled"],
            default="enabled",
            help="Administrative control of subcloud group.",
        )

        self.add_argument(
            "--max-subcloud-rehoming",
            required=False,
            type=int,
            default=10,
            help="Maximum number of subclouds to migrate in parallel",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        kwargs = {}

        kwargs["peer-group-name"] = parsed_args.peer_group_name

        if parsed_args.group_state is not None:
            kwargs["group-state"] = parsed_args.group_state

        if parsed_args.max_subcloud_rehoming is not None:
            kwargs["max-subcloud-rehoming"] = parsed_args.max_subcloud_rehoming

        return subcloud_peer_group_manager.add_subcloud_peer_group(**kwargs)


class DeleteSubcloudPeerGroup(ConfirmationMixin, command.Command):
    """Delete subcloud peer group details from the database."""

    requires_confirmation = True

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "group", help="Name or ID of the subcloud peer group to delete."
        )
        return parser

    def take_action(self, parsed_args):
        super().take_action(parsed_args)
        subcloud_peer_group_ref = parsed_args.group
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        try:
            subcloud_peer_group_manager.delete_subcloud_peer_group(
                subcloud_peer_group_ref
            )
        except Exception as exc:
            print(exc)
            msg = f"Unable to delete subcloud peer group {subcloud_peer_group_ref}"
            raise exceptions.DCManagerClientException(msg)


class ShowSubcloudPeerGroup(base.DCManagerShowOne):
    """Show the details of a subcloud peer group."""

    def _get_format_function(self):
        return group_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "group", help="Name or ID of subcloud peer group to view the details."
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_ref = parsed_args.group
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        return subcloud_peer_group_manager.subcloud_peer_group_detail(
            subcloud_peer_group_ref
        )


class ListSubcloudPeerGroup(base.DCManagerLister):
    """List subcloud peer groups."""

    def _get_format_function(self):
        return group_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        return subcloud_peer_group_manager.list_subcloud_peer_groups()


class ListSubcloudPeerGroupSubclouds(base.DCManagerLister):
    """List subclouds referencing a subcloud peer group."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        self.add_argument(
            "group",
            help="Name or ID of subcloud peer group to list " "associated subclouds.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_ref = parsed_args.group
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        return subcloud_peer_group_manager.subcloud_peer_group_list_subclouds(
            subcloud_peer_group_ref
        )


class UpdateSubcloudPeerGroup(base.DCManagerShowOne):
    """Update attributes of a subcloud peer group."""

    def _get_format_function(self):
        return group_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "group", help="Name or ID of the subcloud peer group to update."
        )

        self.add_argument(
            "--peer-group-name",
            required=False,
            help="Name for the new subcloud peer group.",
        )

        self.add_argument(
            "--group-state",
            required=False,
            choices=["enabled", "disabled"],
            help="Administrative control of subcloud peer group.",
        )

        self.add_argument(
            "--max-subcloud-rehoming",
            required=False,
            type=int,
            help="Maximum number of subclouds to migrate in parallel",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_ref = parsed_args.group
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        kwargs = {}

        if parsed_args.peer_group_name is not None:
            kwargs["peer-group-name"] = parsed_args.peer_group_name

        if parsed_args.group_state is not None:
            kwargs["group-state"] = parsed_args.group_state

        if parsed_args.max_subcloud_rehoming is not None:
            kwargs["max-subcloud-rehoming"] = parsed_args.max_subcloud_rehoming

        if len(kwargs) == 0:
            error_msg = "Nothing to update"
            raise exceptions.DCManagerClientException(error_msg)

        try:
            return subcloud_peer_group_manager.update_subcloud_peer_group(
                subcloud_peer_group_ref, **kwargs
            )
        except Exception as exc:
            print(exc)
            msg = f"Unable to update subcloud peer group {subcloud_peer_group_ref}"
            raise exceptions.DCManagerClientException(msg)


def detail_status_format(subcloud_peer_group_status=None):
    # Include all the fields in peer_group_format
    # plus some additional fields
    columns = (
        "peer_group_id",
        "peer_group_name",
        "total_subclouds",
        "complete",
        "waiting_for_migrate",
        "rehoming",
        "rehome_failed",
        "managed",
        "unmanaged",
    )
    if subcloud_peer_group_status:
        data = (
            subcloud_peer_group_status["peer_group_id"],
            subcloud_peer_group_status["peer_group_name"],
            subcloud_peer_group_status["total_subclouds"],
            subcloud_peer_group_status["complete"],
            subcloud_peer_group_status["waiting_for_migrate"],
            subcloud_peer_group_status["rehoming"],
            subcloud_peer_group_status["rehome_failed"],
            subcloud_peer_group_status["managed"],
            subcloud_peer_group_status["unmanaged"],
        )
    else:
        data = (tuple("<none>" for _ in range(len(columns))),)
    return columns, data


class StatusSubcloudPeerGroup(base.DCManagerShowOne):
    """Show a summary of subcloud statuses within a peer group."""

    def _get_format_function(self):
        return detail_status_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "group", help="Name or ID of subcloud peer group to view the status."
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_peer_group_ref = parsed_args.group
        subcloud_peer_group_manager = (
            self.app.client_manager.subcloud_peer_group_manager
        )
        return subcloud_peer_group_manager.subcloud_peer_group_status(
            subcloud_peer_group_ref
        )
