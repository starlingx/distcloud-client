#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import copy

import mock
from oslo_utils import timeutils

from dcmanagerclient.api.v1 import system_peer_manager as spm
from dcmanagerclient.api.v1.subcloud_peer_group_manager import (
    SubcloudPeerGroup as Peergroup,
)
from dcmanagerclient.commands.v1 import system_peer_manager as system_peer_cmd
from dcmanagerclient.tests import base

# Sample System Peer data
ID = "2"
SYSTEM_PEER_UUID = "test1234-0dfd-46cd-9a93-e3c2b74ef20f"
SYSTEM_PEER_NAME = "SystemPeer1"
MANAGER_ENDPOINT = "http://127.0.0.1:5000"
MANAGER_USERNAME = "admin"
MANAGER_PASSWORD = "password"
ADMINISTRATIVE_STATE = "enabled"
HEARTBEAT_INTERVAL = 10
HEARTBEAT_FAILURE_THRESHOLD = 3
HEARTBEAT_FAILURES_POLICY = "alarm"
HEARTBEAT_MAINTENANCE_TIMEOUT = 600
AVAILABILITY_STATE = "available"
PEER_CONTROLLER_GATEWAY_IP = "128.128.128.1"
TIME_NOW = timeutils.utcnow().isoformat()
NEW_PEER_CONTROLLER_GATEWAY_IP = "128.1.1.1"

# Sample Subcloud Peer Group data
PG_ID = "1"
PG_NAME = "SubcloudPeerGroup1"
PG_GROUP_PRIORITY = "99"
PG_GROUP_STATE = "disabled"
PG_MAX_SUBCLOUD_REHOMING = "10"
PG_SYSTEM_LEADER_ID = "d9dea83f-f271-470d-9cce-44b0162a800b"
PG_SYSTEM_LEADER_NAME = "DC-1"
PG_CREATED_AT = TIME_NOW
PG_UPDATED_AT = TIME_NOW

SYSTEM_PEER_DICT = {
    "PEER_ID": ID,
    "PEER_UUID": SYSTEM_PEER_UUID,
    "PEER_NAME": SYSTEM_PEER_NAME,
    "MANAGER_ENDPOINT": MANAGER_ENDPOINT,
    "MANAGER_USERNAME": MANAGER_USERNAME,
    "ADMINISTRATIVE_STATE": ADMINISTRATIVE_STATE,
    "HEARTBEAT_INTERVAL": HEARTBEAT_INTERVAL,
    "HEARTBEAT_FAILURE_THRESHOLD": HEARTBEAT_FAILURE_THRESHOLD,
    "HEARTBEAT_FAILURE_POLICY": HEARTBEAT_FAILURES_POLICY,
    "HEARTBEAT_MAINTENANCE_TIMEOUT": HEARTBEAT_MAINTENANCE_TIMEOUT,
    "AVAILABILITY_STATE": AVAILABILITY_STATE,
    "PEER_CONTROLLER_GATEWAY_IP": PEER_CONTROLLER_GATEWAY_IP,
    "CREATED_AT": TIME_NOW,
    "UPDATED_AT": TIME_NOW,
}

# System Peer CLI resource object
SYSTEM_PEER = spm.SystemPeer(
    mock,
    peer_id=SYSTEM_PEER_DICT["PEER_ID"],
    peer_name=SYSTEM_PEER_DICT["PEER_NAME"],
    peer_uuid=SYSTEM_PEER_DICT["PEER_UUID"],
    manager_endpoint=SYSTEM_PEER_DICT["MANAGER_ENDPOINT"],
    manager_username=SYSTEM_PEER_DICT["MANAGER_USERNAME"],
    administrative_state=SYSTEM_PEER_DICT["ADMINISTRATIVE_STATE"],
    heartbeat_interval=SYSTEM_PEER_DICT["HEARTBEAT_INTERVAL"],
    heartbeat_failure_threshold=SYSTEM_PEER_DICT["HEARTBEAT_FAILURE_THRESHOLD"],
    heartbeat_failure_policy=SYSTEM_PEER_DICT["HEARTBEAT_FAILURE_POLICY"],
    heartbeat_maintenance_timeout=SYSTEM_PEER_DICT["HEARTBEAT_MAINTENANCE_TIMEOUT"],
    availability_state=SYSTEM_PEER_DICT["AVAILABILITY_STATE"],
    peer_controller_gateway_address=SYSTEM_PEER_DICT["PEER_CONTROLLER_GATEWAY_IP"],
    created_at=SYSTEM_PEER_DICT["CREATED_AT"],
    updated_at=SYSTEM_PEER_DICT["UPDATED_AT"],
)

# Subcloud Peer Group CLI resource object
PEER_GROUP = Peergroup(
    mock,
    PG_ID,
    PG_NAME,
    PG_GROUP_PRIORITY,
    PG_GROUP_STATE,
    PG_SYSTEM_LEADER_ID,
    PG_SYSTEM_LEADER_NAME,
    PG_MAX_SUBCLOUD_REHOMING,
    PG_CREATED_AT,
    PG_UPDATED_AT,
)
PG_TUPLE = (
    PG_ID,
    PG_NAME,
    PG_GROUP_PRIORITY,
    PG_GROUP_STATE,
    PG_SYSTEM_LEADER_ID,
    PG_SYSTEM_LEADER_NAME,
    PG_MAX_SUBCLOUD_REHOMING,
)


class TestCLISystemPeerManagerV1(base.BaseCommandTest):

    def setUp(self):
        super().setUp()
        # The client is the system_peer_manager
        self.client = self.app.client_manager.system_peer_manager

    def test_list_system_peers(self):
        self.client.system_peer_manager.list_system_peers.return_value = [
            SYSTEM_PEER
        ]
        actual_call = self.call(system_peer_cmd.ListSystemPeer)
        self.assertEqual(
            [
                (
                    ID,
                    SYSTEM_PEER_UUID,
                    SYSTEM_PEER_NAME,
                    MANAGER_ENDPOINT,
                    PEER_CONTROLLER_GATEWAY_IP,
                )
            ],
            actual_call[1],
        )

    def test_list_system_peers_empty(self):
        self.client.system_peer_manager.list_system_peers.return_value = []
        actual_call = self.call(system_peer_cmd.ListSystemPeer)
        self.assertEqual((tuple("<none>" for _ in range(5)),), actual_call[1])

    def test_delete_system_peer_by_id(self):
        self.call(system_peer_cmd.DeleteSystemPeer, app_args=[ID])
        self.client.system_peer_manager.delete_system_peer.assert_called_once_with(
            ID
        )

    def test_delete_system_peer_without_id(self):
        self.assertRaises(
            SystemExit, self.call, system_peer_cmd.DeleteSystemPeer, app_args=[]
        )

    def test_show_system_peer_with_id(self):
        self.client.system_peer_manager.system_peer_detail.return_value = [
            SYSTEM_PEER
        ]
        actual_call = self.call(system_peer_cmd.ShowSystemPeer, app_args=[ID])
        self.assertEqual(
            (
                ID,
                SYSTEM_PEER_UUID,
                SYSTEM_PEER_NAME,
                MANAGER_ENDPOINT,
                MANAGER_USERNAME,
                PEER_CONTROLLER_GATEWAY_IP,
                ADMINISTRATIVE_STATE,
                HEARTBEAT_INTERVAL,
                HEARTBEAT_FAILURE_THRESHOLD,
                HEARTBEAT_FAILURES_POLICY,
                HEARTBEAT_MAINTENANCE_TIMEOUT,
                AVAILABILITY_STATE,
                TIME_NOW,
                TIME_NOW,
            ),
            actual_call[1],
        )

    def test_show_system_peer_without_id(self):
        self.client.system_peer_manager.system_peer_detail.return_value = []
        actual_call = self.call(system_peer_cmd.ShowSystemPeer, app_args=[ID])
        self.assertEqual((tuple("<none>" for _ in range(14)),), actual_call[1])

    def test_list_system_peer_subcloud_peer_groups(self):
        self.client.system_peer_manager.system_peer_list_peer_groups.return_value = [
            PEER_GROUP
        ]
        actual_call = self.call(
            system_peer_cmd.ListSystemPeerSubcloudPeerGroups, app_args=[ID]
        )
        self.assertEqual([PG_TUPLE], actual_call[1])

    def test_add_system_peer(self):
        self.client.system_peer_manager.add_system_peer.return_value = [SYSTEM_PEER]

        actual_call = self.call(
            system_peer_cmd.AddSystemPeer,
            app_args=[
                "--peer-uuid",
                SYSTEM_PEER_UUID,
                "--peer-name",
                SYSTEM_PEER_NAME,
                "--manager-endpoint",
                MANAGER_ENDPOINT,
                "--manager-username",
                MANAGER_USERNAME,
                "--manager-password",
                MANAGER_PASSWORD,
                "--heartbeat-interval",
                str(HEARTBEAT_INTERVAL),
                "--heartbeat-failure-threshold",
                str(HEARTBEAT_FAILURE_THRESHOLD),
                "--heartbeat-failure-policy",
                HEARTBEAT_FAILURES_POLICY,
                "--heartbeat-maintenance-timeout",
                str(HEARTBEAT_MAINTENANCE_TIMEOUT),
                "--peer-controller-gateway-address",
                PEER_CONTROLLER_GATEWAY_IP,
                "--administrative-state",
                ADMINISTRATIVE_STATE,
            ],
        )
        self.assertEqual(
            (
                ID,
                SYSTEM_PEER_UUID,
                SYSTEM_PEER_NAME,
                MANAGER_ENDPOINT,
                MANAGER_USERNAME,
                PEER_CONTROLLER_GATEWAY_IP,
                ADMINISTRATIVE_STATE,
                HEARTBEAT_INTERVAL,
                HEARTBEAT_FAILURE_THRESHOLD,
                HEARTBEAT_FAILURES_POLICY,
                HEARTBEAT_MAINTENANCE_TIMEOUT,
                AVAILABILITY_STATE,
                TIME_NOW,
                TIME_NOW,
            ),
            actual_call[1],
        )

    def test_update_system_peer(self):
        UPDATED_SYSTEM_PEER = copy.copy(SYSTEM_PEER)
        UPDATED_SYSTEM_PEER.peer_controller_gateway_ip = (
            NEW_PEER_CONTROLLER_GATEWAY_IP
        )
        self.client.system_peer_manager.update_system_peer.return_value = [
            UPDATED_SYSTEM_PEER
        ]
        actual_call = self.call(
            system_peer_cmd.UpdateSystemPeer,
            app_args=[
                SYSTEM_PEER.peer_id,
                "--peer-controller-gateway-address",
                NEW_PEER_CONTROLLER_GATEWAY_IP,
            ],
        )
        self.assertEqual(
            (
                ID,
                SYSTEM_PEER_UUID,
                SYSTEM_PEER_NAME,
                MANAGER_ENDPOINT,
                MANAGER_USERNAME,
                PEER_CONTROLLER_GATEWAY_IP,
                ADMINISTRATIVE_STATE,
                HEARTBEAT_INTERVAL,
                HEARTBEAT_FAILURE_THRESHOLD,
                HEARTBEAT_FAILURES_POLICY,
                HEARTBEAT_MAINTENANCE_TIMEOUT,
                AVAILABILITY_STATE,
                TIME_NOW,
                TIME_NOW,
            ),
            actual_call[1],
        )
