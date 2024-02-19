#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from osc_lib.command import command

from dcmanagerclient import exceptions
from dcmanagerclient.commands.v1 import base


def association_format(peer_group_association=None):
    columns = (
        "id",
        "peer_group_id",
        "system_peer_id",
        "type",
        "sync_status",
        "peer_group_priority",
    )

    if peer_group_association:
        data = (
            peer_group_association.association_id,
            peer_group_association.peer_group_id,
            peer_group_association.system_peer_id,
            peer_group_association.association_type,
            peer_group_association.sync_status,
            peer_group_association.peer_group_priority,
        )

    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def detail_association_format(peer_group_association=None):
    # Include all the fields in detail_association_format
    # plus some additional fields
    columns = (
        "id",
        "peer_group_id",
        "system_peer_id",
        "association_type",
        "sync_status",
        "peer_group_priority",
        "sync_message",
        "created_at",
        "updated_at",
    )

    if peer_group_association:
        data = (
            peer_group_association.association_id,
            peer_group_association.peer_group_id,
            peer_group_association.system_peer_id,
            peer_group_association.association_type,
            peer_group_association.sync_status,
            peer_group_association.peer_group_priority,
            peer_group_association.sync_message,
            peer_group_association.created_at,
            peer_group_association.updated_at,
        )
    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


class AddPeerGroupAssociation(base.DCManagerShowOne):
    """Add a new peer group association."""

    def _get_format_function(self):
        return detail_association_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--peer-group-id", required=True, help="Subcloud peer group ID."
        )

        parser.add_argument(
            "--system-peer-id", required=True, help="System Peer ID."
        )

        parser.add_argument(
            "--peer-group-priority",
            required=True,
            type=int,
            help="Priority of this peer group.",
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.peer_group_association_manager
        kwargs = {
            "peer_group_id": parsed_args.peer_group_id,
            "system_peer_id": parsed_args.system_peer_id,
            "peer_group_priority": parsed_args.peer_group_priority,
        }
        return dcmanager_client.peer_group_association_manager.\
            add_peer_group_association(**kwargs)


class ListPeerGroupAssociation(base.DCManagerLister):
    """List peer group associations."""

    def _get_format_function(self):
        return association_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.peer_group_association_manager
        return dcmanager_client.peer_group_association_manager.\
            list_peer_group_associations()


class ShowPeerGroupAssociation(base.DCManagerShowOne):
    """Show the details of a peer group association."""

    def _get_format_function(self):
        return detail_association_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "id", help="ID of the peer group association to view the details."
        )

        return parser

    def _get_resources(self, parsed_args):
        association_ref = parsed_args.id
        dcmanager_client = self.app.client_manager.peer_group_association_manager
        return dcmanager_client.peer_group_association_manager.\
            peer_group_association_detail(association_ref)


class SyncPeerGroupAssociation(base.DCManagerShowOne):
    """Sync the subcloud peer group to peer site."""

    def _get_format_function(self):
        return detail_association_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("id", help="ID of the peer group association to sync.")

        return parser

    def _get_resources(self, parsed_args):
        association_ref = parsed_args.id
        dcmanager_client = self.app.client_manager.peer_group_association_manager
        return dcmanager_client.peer_group_association_manager.\
            sync_peer_group_association(association_ref)


class DeletePeerGroupAssociation(command.Command):
    """Delete peer group association from the database."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("id", help="ID of the peer group association to delete.")
        return parser

    def take_action(self, parsed_args):
        dcmanager_client = self.app.client_manager.peer_group_association_manager
        try:
            dcmanager_client.peer_group_association_manager.\
                delete_peer_group_association(parsed_args.id)
        except Exception as e:
            print(e)
            msg = f"Unable to delete peer group association {parsed_args.id}"
            raise exceptions.DCManagerClientException(msg)


class UpdatePeerGroupAssociation(base.DCManagerShowOne):
    """Update attributes of a peer group association."""

    def _get_format_function(self):
        return detail_association_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("id", help="ID of the peer group association to update.")

        parser.add_argument(
            "--peer-group-priority",
            required=True,
            type=int,
            help="Priority of the subcloud peer group in this association.",
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.peer_group_association_manager

        kwargs = {"peer_group_priority": parsed_args.peer_group_priority}
        try:
            return dcmanager_client.peer_group_association_manager.\
                update_peer_group_association(parsed_args.id, **kwargs)
        except Exception as e:
            print(e)
            msg = f"Unable to update peer group association {parsed_args.id}"
            raise exceptions.DCManagerClientException(msg)
