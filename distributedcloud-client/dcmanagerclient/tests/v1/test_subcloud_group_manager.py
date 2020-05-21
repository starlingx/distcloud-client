# Copyright (c) 2017 Ericsson AB.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Copyright (c) 2017-2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import copy
import mock

from oslo_utils import timeutils

from dcmanagerclient.api.v1 import subcloud_group_manager as zm
from dcmanagerclient.commands.v1 \
    import subcloud_group_manager as subcloud_group_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1 import test_subcloud_manager as tsm


ID = '2'
NAME = 'GroupX'
DESCRIPTION = 'Custom subcloud group'
APPLY_TYPE = 'parallel'
MAX_PARALLEL_SUBCLOUDS = 3
TIME_NOW = timeutils.utcnow().isoformat()
NEW_DESCRIPTION = 'Slightly different subcloud group'

SUBCLOUD_GROUP_DICT = {
    'GROUP_ID': ID,
    'NAME': NAME,
    'DESCRIPTION': DESCRIPTION,
    'APPLY_TYPE': APPLY_TYPE,
    'MAX_PARALLEL_SUBCLOUDS': MAX_PARALLEL_SUBCLOUDS,
    'CREATED_AT': TIME_NOW,
    'UPDATED_AT': TIME_NOW
}

SUBCLOUD_GROUP = zm.SubcloudGroup(
    mock,
    group_id=SUBCLOUD_GROUP_DICT['GROUP_ID'],
    name=SUBCLOUD_GROUP_DICT['NAME'],
    description=SUBCLOUD_GROUP_DICT['DESCRIPTION'],
    update_apply_type=SUBCLOUD_GROUP_DICT['APPLY_TYPE'],
    max_parallel_subclouds=SUBCLOUD_GROUP_DICT['MAX_PARALLEL_SUBCLOUDS'],
    created_at=SUBCLOUD_GROUP_DICT['CREATED_AT'],
    updated_at=SUBCLOUD_GROUP_DICT['UPDATED_AT']
)


class TestCLISubcloudGroupManagerV1(base.BaseCommandTest):

    def setUp(self):
        super(TestCLISubcloudGroupManagerV1, self).setUp()
        # The client is the subcloud_group_manager
        self.client = self.app.client_manager.subcloud_group_manager

    def test_list_subcloud_groups(self):
        self.client.subcloud_group_manager.\
            list_subcloud_groups.return_value = [SUBCLOUD_GROUP]
        actual_call = self.call(subcloud_group_cmd.ListSubcloudGroup)
        self.assertEqual([(ID, NAME, DESCRIPTION)],
                         actual_call[1])

    def test_list_subcloud_groups_empty(self):
        self.client.subcloud_group_manager.\
            list_subcloud_groups.return_value = []
        actual_call = self.call(subcloud_group_cmd.ListSubcloudGroup)
        self.assertEqual((('<none>', '<none>', '<none>'),),
                         actual_call[1])

    def test_list_subcloud_group_subclouds(self):
        self.client.subcloud_group_manager.\
            subcloud_group_list_subclouds.return_value = [tsm.SUBCLOUD]
        actual_call = self.call(subcloud_group_cmd.ListSubcloudGroupSubclouds,
                                app_args=[ID])
        self.client.subcloud_group_manager.subcloud_group_list_subclouds.\
            assert_called_once_with(ID)
        self.assertEqual([tsm.DEFAULT_SUBCLOUD_FIELD_RESULT_LIST],
                         actual_call[1])

    def test_delete_subcloud_group_by_id(self):
        self.call(subcloud_group_cmd.DeleteSubcloudGroup, app_args=[ID])
        self.client.subcloud_group_manager.delete_subcloud_group.\
            assert_called_once_with(ID)

    def test_delete_subcloud_group_without_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_group_cmd.DeleteSubcloudGroup, app_args=[])

    def test_show_subcloud_group_with_id(self):
        self.client.subcloud_group_manager.subcloud_group_detail.\
            return_value = [SUBCLOUD_GROUP]
        actual_call = self.call(subcloud_group_cmd.ShowSubcloudGroup,
                                app_args=[ID])
        self.assertEqual((ID,
                          NAME,
                          DESCRIPTION,
                          APPLY_TYPE,
                          MAX_PARALLEL_SUBCLOUDS,
                          TIME_NOW,
                          TIME_NOW),
                         actual_call[1])

    def test_show_subcloud_group_without_id(self):
        self.client.subcloud_group_manager.subcloud_group_detail.\
            return_value = []
        actual_call = self.call(subcloud_group_cmd.ShowSubcloudGroup,
                                app_args=[ID])
        self.assertEqual((('<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>', '<none>'),),
                         actual_call[1])

    def test_add_subcloud_group(self):
        self.client.subcloud_group_manager.add_subcloud_group.\
            return_value = [SUBCLOUD_GROUP]

        actual_call = self.call(
            subcloud_group_cmd.AddSubcloudGroup,
            app_args=['--name', NAME,
                      '--description', DESCRIPTION]
        )
        self.assertEqual((ID,
                          NAME,
                          DESCRIPTION,
                          APPLY_TYPE,
                          MAX_PARALLEL_SUBCLOUDS,
                          TIME_NOW,
                          TIME_NOW),
                         actual_call[1])

    def test_update_subcloud_group(self):
        UPDATED_SUBCLOUD = copy.copy(SUBCLOUD_GROUP)
        UPDATED_SUBCLOUD.description = NEW_DESCRIPTION
        self.client.subcloud_group_manager.update_subcloud_group.\
            return_value = [UPDATED_SUBCLOUD]
        actual_call = self.call(
            subcloud_group_cmd.UpdateSubcloudGroup,
            app_args=[SUBCLOUD_GROUP.group_id,
                      '--description', NEW_DESCRIPTION])
        self.assertEqual((ID,
                          NAME,
                          NEW_DESCRIPTION,
                          APPLY_TYPE,
                          MAX_PARALLEL_SUBCLOUDS,
                          TIME_NOW,
                          TIME_NOW),
                         actual_call[1])
