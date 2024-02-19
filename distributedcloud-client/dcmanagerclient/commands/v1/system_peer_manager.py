#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64

from osc_lib.command import command

from dcmanagerclient import exceptions, utils
from dcmanagerclient.commands.v1 import base


def group_format(subcloud_peer_group=None):
    columns = (
        "id",
        "peer_group_name",
        "group_priority",
        "group_state",
        "system_leader_id",
        "system_leader_name",
        "max_subcloud_rehoming",
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
        )

    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def peer_format(system_peer=None):
    columns = (
        "id",
        "peer uuid",
        "peer name",
        "manager endpoint",
        "controller gateway address",
    )

    if system_peer:
        data = (
            system_peer.peer_id,
            system_peer.peer_uuid,
            system_peer.peer_name,
            system_peer.manager_endpoint,
            system_peer.gateway_address,
        )

    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def detail_peer_format(system_peer=None):
    # Include all the fields in peer_format
    # plus some additional fields
    columns = (
        "id",
        "peer uuid",
        "peer name",
        "manager endpoint",
        "manager username",
        "controller gateway address",
        "administrative state",
        "heartbeat interval",
        "heartbeat failure threshold",
        "heartbeat failure policy",
        "heartbeat maintenance timeout",
        "availability state",
        "created_at",
        "updated_at",
    )

    if system_peer:
        data = (
            system_peer.peer_id,
            system_peer.peer_uuid,
            system_peer.peer_name,
            system_peer.manager_endpoint,
            system_peer.manager_username,
            system_peer.gateway_address,
            system_peer.administrative_state,
            system_peer.heartbeat_interval,
            system_peer.heartbeat_failure_threshold,
            system_peer.heartbeat_failure_policy,
            system_peer.heartbeat_maintenance_timeout,
            system_peer.availability_state,
            system_peer.created_at,
            system_peer.updated_at,
        )
    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


class AddSystemPeer(base.DCManagerShowOne):
    """Add a new system peer."""

    def _get_format_function(self):
        return detail_peer_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--peer-uuid", required=True, help="UUID of the new system peer."
        )

        parser.add_argument(
            "--peer-name", required=True, help="Name for the new system peer."
        )

        parser.add_argument(
            "--manager-endpoint",
            required=True,
            help="URI of DC manager of peer System Controller.",
        )

        parser.add_argument(
            "--peer-controller-gateway-address",
            required=True,
            help="Gateway address of peer site controller node.",
        )

        parser.add_argument(
            "--manager-username",
            required=False,
            default="admin",
            help="Administrative username (default admin).",
        )

        parser.add_argument(
            "--manager-password",
            required=False,
            help="Admin user password for authenticating into the DC manager.",
        )

        parser.add_argument(
            "--administrative-state",
            required=False,
            choices=["enabled", "disabled"],
            default="enabled",
            help="Administrative control of peer state (default enabled).",
        )

        parser.add_argument(
            "--heartbeat-interval",
            required=False,
            default=60,
            help="Interval between heartbeat messages (in seconds) (default \
                  60).",
        )

        parser.add_argument(
            "--heartbeat-failure-threshold",
            required=False,
            default=3,
            help="Consecutive heartbeat failures before failure declared \
                  (default 3).",
        )

        parser.add_argument(
            "--heartbeat-failure-policy",
            required=False,
            choices=["alarm", "rehome", "delegate"],
            default="alarm",
            help="Action to take with failure detection (default alarm).",
        )

        parser.add_argument(
            "--heartbeat-maintenance-timeout",
            required=False,
            default=600,
            help="Overall failure timeout during maintenance state (in \
                  seconds) (default 600).",
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.system_peer_manager
        kwargs = {}

        if parsed_args.peer_uuid is not None:
            kwargs["peer_uuid"] = parsed_args.peer_uuid

        if parsed_args.peer_name is not None:
            kwargs["peer_name"] = parsed_args.peer_name

        if parsed_args.manager_endpoint is not None:
            kwargs["manager_endpoint"] = parsed_args.manager_endpoint

        if parsed_args.manager_username is not None:
            kwargs["manager_username"] = parsed_args.manager_username

        # Prompt the user for the peer's password if it isn't provided
        if parsed_args.manager_password is not None:
            kwargs["manager_password"] = base64.b64encode(
                parsed_args.manager_password.encode("utf-8")
            ).decode("utf-8")
        else:
            password = utils.prompt_for_password(
                password_type=parsed_args.manager_username, item_type="system peer"
            )
            kwargs["manager_password"] = base64.b64encode(
                password.encode("utf-8")
            ).decode("utf-8")

        if parsed_args.peer_controller_gateway_address is not None:
            kwargs["peer_controller_gateway_address"] = (
                parsed_args.peer_controller_gateway_address
            )

        if parsed_args.administrative_state is not None:
            kwargs["administrative_state"] = parsed_args.administrative_state

        if parsed_args.heartbeat_interval is not None:
            kwargs["heartbeat_interval"] = parsed_args.heartbeat_interval

        if parsed_args.heartbeat_failure_threshold is not None:
            kwargs["heartbeat_failure_threshold"] = (
                parsed_args.heartbeat_failure_threshold
            )

        if parsed_args.heartbeat_failure_policy is not None:
            kwargs["heartbeat_failure_policy"] = parsed_args.heartbeat_failure_policy

        if parsed_args.heartbeat_maintenance_timeout is not None:
            kwargs["heartbeat_maintenance_timeout"] = (
                parsed_args.heartbeat_maintenance_timeout
            )
        return dcmanager_client.system_peer_manager.add_system_peer(**kwargs)


class ListSystemPeer(base.DCManagerLister):
    """List system peers."""

    def _get_format_function(self):
        return peer_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.system_peer_manager
        return dcmanager_client.system_peer_manager.list_system_peers()


class ListSystemPeerSubcloudPeerGroups(base.DCManagerLister):
    """List Subcloud Peer Groups referencing a System Peer."""

    def _get_format_function(self):
        return group_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "peer",
            help=(
                "Name or ID or UUID of system peer to list "
                "associated subcloud peer groups."
            ),
        )
        return parser

    def _get_resources(self, parsed_args):
        system_peer_ref = parsed_args.peer
        dcmanager_client = self.app.client_manager.system_peer_manager
        return dcmanager_client.system_peer_manager.system_peer_list_peer_groups(
            system_peer_ref
        )


class ShowSystemPeer(base.DCManagerShowOne):
    """Show the details of a system peer."""

    def _get_format_function(self):
        return detail_peer_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "peer", help="UUID or ID of system peer to view the details."
        )

        return parser

    def _get_resources(self, parsed_args):
        system_peer_ref = parsed_args.peer
        dcmanager_client = self.app.client_manager.system_peer_manager
        return dcmanager_client.system_peer_manager.system_peer_detail(
            system_peer_ref
        )


class DeleteSystemPeer(command.Command):
    """Delete system peer details from the database."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("peer", help="UUID or ID of the system peer to delete.")
        return parser

    def take_action(self, parsed_args):
        system_peer_ref = parsed_args.peer
        dcmanager_client = self.app.client_manager.system_peer_manager
        try:
            dcmanager_client.system_peer_manager.delete_system_peer(system_peer_ref)
        except Exception as e:
            print(e)
            msg = f"Unable to delete system peer {system_peer_ref}"
            raise exceptions.DCManagerClientException(msg)


class UpdateSystemPeer(base.DCManagerShowOne):
    """Update attributes of a system peer."""

    def _get_format_function(self):
        return detail_peer_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("peer", help="UUID or ID of the system peer to update.")

        parser.add_argument(
            "--peer-uuid", required=False, help="UUID of the new system peer."
        )

        parser.add_argument(
            "--peer-name", required=False, help="Name for the new system peer."
        )

        parser.add_argument(
            "--manager-endpoint",
            required=False,
            help="URI of DC manager of peer System Controller.",
        )

        parser.add_argument(
            "--manager-username",
            required=False,
            help="Administrative username (default admin).",
        )

        parser.add_argument(
            "--manager-password",
            required=False,
            nargs="?",
            const=True,
            help="Admin user password for authenticating into the DC manager",
        )

        parser.add_argument(
            "--peer-controller-gateway-address",
            required=False,
            help="Gateway address of peer site controller node.",
        )

        parser.add_argument(
            "--administrative-state",
            required=False,
            choices=["enabled", "disabled"],
            help="Administrative control of peer state (default enabled).",
        )

        parser.add_argument(
            "--heartbeat-interval",
            required=False,
            help=("Interval between heartbeat messages (in seconds) (default 60)."),
        )

        parser.add_argument(
            "--heartbeat-failure-threshold",
            required=False,
            help=(
                "Consecutive heartbeat failures before failure declared "
                "(default 3)."
            ),
        )

        parser.add_argument(
            "--heartbeat-failure-policy",
            required=False,
            choices=["alarm", "rehome", "delegate"],
            help="Action to take with failure detection (default alarm).",
        )

        parser.add_argument(
            "--heartbeat-maintenance-timeout",
            required=False,
            help=(
                "Overall failure timeout during maintenance state (in seconds) "
                "(default 600)."
            ),
        )

        return parser

    def _get_resources(self, parsed_args):
        system_peer_ref = parsed_args.peer
        dcmanager_client = self.app.client_manager.system_peer_manager
        kwargs = {}
        if parsed_args.peer_uuid:
            kwargs["peer_uuid"] = parsed_args.peer_uuid
        if parsed_args.peer_name:
            kwargs["peer_name"] = parsed_args.peer_name
        if parsed_args.manager_endpoint:
            kwargs["manager_endpoint"] = parsed_args.manager_endpoint
        if parsed_args.manager_username:
            kwargs["manager_username"] = parsed_args.manager_username
        if parsed_args.manager_password:
            if parsed_args.manager_password is True:
                password = utils.prompt_for_password(
                    password_type="update", item_type="system peer"
                )
                kwargs["manager_password"] = base64.b64encode(
                    password.encode("utf-8")
                ).decode("utf-8")
            else:
                kwargs["manager_password"] = base64.b64encode(
                    parsed_args.manager_password.encode("utf-8")
                ).decode("utf-8")
        if parsed_args.peer_controller_gateway_address:
            kwargs["peer_controller_gateway_address"] = (
                parsed_args.peer_controller_gateway_address
            )
        if parsed_args.administrative_state:
            kwargs["administrative_state"] = parsed_args.administrative_state
        if parsed_args.heartbeat_interval:
            kwargs["heartbeat_interval"] = parsed_args.heartbeat_interval
        if parsed_args.heartbeat_failure_threshold:
            kwargs["heartbeat_failure_threshold"] = (
                parsed_args.heartbeat_failure_threshold
            )
        if parsed_args.heartbeat_failure_policy:
            kwargs["heartbeat_failure_policy"] = parsed_args.heartbeat_failure_policy
        if parsed_args.heartbeat_maintenance_timeout:
            kwargs["heartbeat_maintenance_timeout"] = (
                parsed_args.heartbeat_maintenance_timeout
            )
        if len(kwargs) == 0:
            error_msg = "Nothing to update"
            raise exceptions.DCManagerClientException(error_msg)

        try:
            return dcmanager_client.system_peer_manager.update_system_peer(
                system_peer_ref, **kwargs
            )
        except Exception as e:
            print(e)
            msg = f"Unable to update system peer {system_peer_ref}"
            raise exceptions.DCManagerClientException(msg)
