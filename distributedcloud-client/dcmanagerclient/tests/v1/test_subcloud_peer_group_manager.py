# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import mock
from oslo_utils import timeutils

from dcmanagerclient.api.v1.subcloud_peer_group_manager \
    import SubcloudPeerGroup as Peergroup
from dcmanagerclient.commands.v1 \
    import subcloud_peer_group_manager as subcloud_peer_group_cmd
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base

FAKE_MANAGER = None
PG_ID = "1"
PG_NAME = "test-pg-name"
PG_GROUP_PRIORITY = "99"
PG_GROUP_STATE = "disabled"
PG_MAX_SUBCLOUD_REHOMING = "10"
PG_SYSTEM_LEADER_ID = "d9dea83f-f271-470d-9cce-44b0162a800b"
PG_SYSTEM_LEADER_NAME = "dc-1"
TIME_NOW = timeutils.utcnow().isoformat()
PG_CREATED_AT = TIME_NOW
PG_UPDATED_AT = TIME_NOW
SubcloudPeerGroup = Peergroup(
    mock,
    PG_ID,
    PG_NAME,
    PG_GROUP_PRIORITY,
    PG_GROUP_STATE,
    PG_SYSTEM_LEADER_ID,
    PG_SYSTEM_LEADER_NAME,
    PG_MAX_SUBCLOUD_REHOMING,
    PG_CREATED_AT,
    PG_UPDATED_AT
)

PG_TUPLE = (PG_ID,
            PG_NAME,
            PG_GROUP_PRIORITY,
            PG_GROUP_STATE,
            PG_SYSTEM_LEADER_ID,
            PG_SYSTEM_LEADER_NAME,
            PG_MAX_SUBCLOUD_REHOMING,
            )
PG_TUPLE_WITH_DATE = PG_TUPLE + (PG_CREATED_AT, PG_UPDATED_AT)


class TestCLISubcloudPeerGroupManager(base.BaseCommandTest):
    def setUp(self):
        super(TestCLISubcloudPeerGroupManager, self).setUp()
        # The client is the subcloud_peer_group_manager
        self.client = self.app.client_manager.subcloud_peer_group_manager

    def test_list_subcloud_peer_groups(self):
        self.client.subcloud_peer_group_manager.\
            list_subcloud_peer_groups.return_value =\
            [SubcloudPeerGroup]
        actual_call = self.call(subcloud_peer_group_cmd.ListSubcloudPeerGroup)
        self.assertEqual([PG_TUPLE_WITH_DATE],
                         actual_call[1])

    def test_show_subcloud_peer_group(self):
        self.client.subcloud_peer_group_manager.\
            subcloud_peer_group_detail.return_value =\
            [SubcloudPeerGroup]
        actual_call = self.call(subcloud_peer_group_cmd.ShowSubcloudPeerGroup,
                                app_args=[PG_ID])
        self.assertEqual(PG_TUPLE_WITH_DATE, actual_call[1])

    def test_list_subcloud_peer_group_subclouds(self):
        self.client.subcloud_peer_group_manager.\
            subcloud_peer_group_list_subclouds.return_value = \
            [base.SUBCLOUD_RESOURCE_WITH_PEERID_REHOME_DATA]
        actual_call = self.call(
            subcloud_peer_group_cmd.ListSubcloudPeerGroupSubclouds,
            app_args=[base.ID])
        self.assertEqual([
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA],
            actual_call[1])

    def test_add_subcloud_peer_group(self):
        self.client.subcloud_peer_group_manager.add_subcloud_peer_group.\
            return_value = [SubcloudPeerGroup]
        actual_call1 = self.call(
            subcloud_peer_group_cmd.AddSubcloudPeerGroup, app_args=[
                '--peer-group-name', PG_NAME
            ])

        actual_call2 = self.call(
            subcloud_peer_group_cmd.AddSubcloudPeerGroup, app_args=[
                '--peer-group-name', PG_NAME,
                '--group-priority', PG_GROUP_PRIORITY,
                '--group-state', PG_GROUP_STATE,
                '--max-subcloud-rehoming', PG_MAX_SUBCLOUD_REHOMING
            ])
        self.assertEqual(
            PG_TUPLE_WITH_DATE,
            actual_call1[1])
        self.assertEqual(
            PG_TUPLE_WITH_DATE,
            actual_call2[1])

    def test_delete_subcloud_peer_group(self):
        self.call(subcloud_peer_group_cmd.DeleteSubcloudPeerGroup,
                  app_args=[PG_ID])
        self.client.subcloud_peer_group_manager.delete_subcloud_peer_group.\
            assert_called_once_with(PG_ID)

    def test_update_subcloud_peer_group(self):
        self.client.subcloud_peer_group_manager.update_subcloud_peer_group.\
            return_value = [SubcloudPeerGroup]
        actual_call = self.call(
            subcloud_peer_group_cmd.UpdateSubcloudPeerGroup,
            app_args=[
                base.ID,
                '--peer-group-name', PG_NAME,
                '--group-priority', PG_GROUP_PRIORITY,
                '--group-state', PG_GROUP_STATE,
                '--max-subcloud-rehoming', PG_MAX_SUBCLOUD_REHOMING])
        self.assertEqual(
            (PG_TUPLE_WITH_DATE),
            actual_call[1])

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_peer_group_cmd.UpdateSubcloudPeerGroup,
                              app_args=[base.ID])
        self.assertTrue('Nothing to update' in str(e))
