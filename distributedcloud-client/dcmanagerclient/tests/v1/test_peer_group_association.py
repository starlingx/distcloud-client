#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import copy

import mock
from oslo_utils import timeutils

from dcmanagerclient.api.v1.peer_group_association_manager import (
    PeerGroupAssociation as PeerAssociation,
)
from dcmanagerclient.commands.v1 import (
    peer_group_association_manager as peer_group_association_cmd,
)
from dcmanagerclient.tests import base

PEER_GROUP_ASSOCIATION_ID = "1"
PEER_GROUP_ID = "2"
SYSTEM_PEER_ID = "3"
PG_GROUP_PRIORITY = "99"
ASSOCIATION_TYPE = "primary"
SYNC_STATUS = "synced"
SYNC_MESSAGE = "None"
PG_GROUP_PRIORITY_UPDATED = "1"
TIME_NOW = timeutils.utcnow().isoformat()
CREATED_AT = TIME_NOW
UPDATED_AT = TIME_NOW

PEER_GROUP_ASSOCIATION = PeerAssociation(
    mock,
    PEER_GROUP_ASSOCIATION_ID,
    PEER_GROUP_ID,
    SYSTEM_PEER_ID,
    PG_GROUP_PRIORITY,
    ASSOCIATION_TYPE,
    SYNC_STATUS,
    SYNC_MESSAGE,
    CREATED_AT,
    UPDATED_AT,
)

PEER_GROUP_ASSOCIATION_TUPLE = (
    PEER_GROUP_ASSOCIATION_ID,
    PEER_GROUP_ID,
    SYSTEM_PEER_ID,
    ASSOCIATION_TYPE,
    SYNC_STATUS,
    PG_GROUP_PRIORITY,
)

PEER_GROUP_ASSOCIATION_DETAIL_TUPLE = PEER_GROUP_ASSOCIATION_TUPLE + (
    SYNC_MESSAGE,
    CREATED_AT,
    UPDATED_AT,
)

PEER_GROUP_ASSOCIATION_TUPLE_UPDATED = (
    PEER_GROUP_ASSOCIATION_ID,
    PEER_GROUP_ID,
    SYSTEM_PEER_ID,
    ASSOCIATION_TYPE,
    SYNC_STATUS,
    PG_GROUP_PRIORITY_UPDATED,
    SYNC_MESSAGE,
    CREATED_AT,
    UPDATED_AT,
)


class TestCLIPeerGroupAssociationV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        # The client is the peer_group_association_manager
        self.client = self.app.client_manager.peer_group_association_manager

    def test_list_peer_group_association(self):
        self.client.list_peer_group_associations.return_value = [
            PEER_GROUP_ASSOCIATION
        ]
        actual_call = self.call(peer_group_association_cmd.ListPeerGroupAssociation)
        self.assertEqual([PEER_GROUP_ASSOCIATION_TUPLE], actual_call[1])

    def test_list_peer_group_association_empty(self):
        self.client.list_peer_group_associations.return_value = []
        actual_call = self.call(peer_group_association_cmd.ListPeerGroupAssociation)
        self.assertEqual(
            (tuple("<none>" for _ in range(len(PEER_GROUP_ASSOCIATION_TUPLE))),),
            actual_call[1],
        )

    def test_add_peer_group_association(self):
        self.client.add_peer_group_association.return_value = [
            PEER_GROUP_ASSOCIATION
        ]
        actual_call = self.call(
            peer_group_association_cmd.AddPeerGroupAssociation,
            app_args=[
                "--peer-group-id",
                PEER_GROUP_ID,
                "--system-peer-id",
                SYSTEM_PEER_ID,
                "--peer-group-priority",
                PG_GROUP_PRIORITY,
            ],
        )
        self.assertEqual(PEER_GROUP_ASSOCIATION_DETAIL_TUPLE, actual_call[1])

    def test_show_peer_group_association(self):
        self.client.peer_group_association_detail.return_value = [
            PEER_GROUP_ASSOCIATION
        ]
        actual_call = self.call(
            peer_group_association_cmd.ShowPeerGroupAssociation,
            app_args=[PEER_GROUP_ASSOCIATION_ID],
        )
        self.assertEqual(
            (
                PEER_GROUP_ASSOCIATION_ID,
                PEER_GROUP_ID,
                SYSTEM_PEER_ID,
                ASSOCIATION_TYPE,
                SYNC_STATUS,
                PG_GROUP_PRIORITY,
                SYNC_MESSAGE,
                CREATED_AT,
                UPDATED_AT,
            ),
            actual_call[1],
        )

    def test_show_peer_group_association_without_id(self):
        self.client.peer_group_association_detail.return_value = []
        self.assertRaises(
            SystemExit,
            self.call,
            peer_group_association_cmd.ShowPeerGroupAssociation,
            app_args=[],
        )

    def test_delete_peer_group_association(self):
        self.call(
            peer_group_association_cmd.DeletePeerGroupAssociation,
            app_args=[PEER_GROUP_ASSOCIATION_ID],
        )
        self.client.delete_peer_group_association.assert_called_once_with(
            PEER_GROUP_ASSOCIATION_ID
        )

    def test_delete_peer_group_association_without_id(self):
        self.assertRaises(
            SystemExit,
            self.call,
            peer_group_association_cmd.DeletePeerGroupAssociation,
            app_args=[],
        )

    def test_update_peer_group_association(self):
        updated_peed_group_association = copy.copy(PEER_GROUP_ASSOCIATION)
        updated_peed_group_association.peer_group_priority = (
            PG_GROUP_PRIORITY_UPDATED
        )
        self.client.update_peer_group_association.return_value = [
            updated_peed_group_association
        ]
        actual_call = self.call(
            peer_group_association_cmd.UpdatePeerGroupAssociation,
            app_args=[
                PEER_GROUP_ASSOCIATION_ID,
                "--peer-group-priority",
                PG_GROUP_PRIORITY_UPDATED,
            ],
        )
        self.assertEqual((PEER_GROUP_ASSOCIATION_TUPLE_UPDATED), actual_call[1])

    def test_update_peer_group_association_without_priority(self):
        self.client.update_peer_group_association.return_value = [
            PEER_GROUP_ASSOCIATION
        ]
        self.assertRaises(
            SystemExit,
            self.call,
            peer_group_association_cmd.UpdatePeerGroupAssociation,
            app_args=[PEER_GROUP_ID],
        )

    def test_sync_peer_group_association(self):
        self.client.sync_peer_group_association.return_value = [
            PEER_GROUP_ASSOCIATION
        ]
        actual_call = self.call(
            peer_group_association_cmd.SyncPeerGroupAssociation,
            app_args=[PEER_GROUP_ASSOCIATION_ID],
        )
        self.assertEqual((PEER_GROUP_ASSOCIATION_DETAIL_TUPLE), actual_call[1])
