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
# Copyright (c) 2017 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import copy
import mock

from oslo_utils import timeutils

from dcmanagerclient.api.v1 import subcloud_manager as sm
from dcmanagerclient.commands.v1 import subcloud_manager as subcloud_cmd
from dcmanagerclient.tests import base

TIME_NOW = timeutils.utcnow().isoformat()
ID = '1'
ID_1 = '2'
NAME = 'subcloud1'
DESCRIPTION = 'subcloud1 description'
LOCATION = 'subcloud1 location'
SOFTWARE_VERSION = '12.34'
MANAGEMENT_STATE = 'unmanaged'
AVAILABILITY_STATUS = 'offline'
MANAGEMENT_SUBNET = '192.168.101.0/24'
MANAGEMENT_START_IP = '192.168.101.2'
MANAGEMENT_END_IP = '192.168.101.50'
MANAGEMENT_GATEWAY_IP = '192.168.101.1'
SYSTEMCONTROLLER_GATEWAY_IP = '192.168.204.101'

SUBCLOUD_DICT = {
    'SUBCLOUD_ID': ID,
    'NAME': NAME,
    'DESCRIPTION': DESCRIPTION,
    'LOCATION': LOCATION,
    'SOFTWARE_VERSION': SOFTWARE_VERSION,
    'MANAGEMENT_STATE': MANAGEMENT_STATE,
    'AVAILABILITY_STATUS': AVAILABILITY_STATUS,
    'MANAGEMENT_SUBNET': MANAGEMENT_SUBNET,
    'MANAGEMENT_START_IP': MANAGEMENT_START_IP,
    'MANAGEMENT_END_IP': MANAGEMENT_END_IP,
    'MANAGEMENT_GATEWAY_IP': MANAGEMENT_GATEWAY_IP,
    'SYSTEMCONTROLLER_GATEWAY_IP': SYSTEMCONTROLLER_GATEWAY_IP,
    'CREATED_AT': TIME_NOW,
    'UPDATED_AT': TIME_NOW
}

SUBCLOUD = sm.Subcloud(
    mock,
    subcloud_id=SUBCLOUD_DICT['SUBCLOUD_ID'],
    name=SUBCLOUD_DICT['NAME'],
    description=SUBCLOUD_DICT['DESCRIPTION'],
    location=SUBCLOUD_DICT['LOCATION'],
    software_version=SUBCLOUD_DICT['SOFTWARE_VERSION'],
    management_state=SUBCLOUD_DICT['MANAGEMENT_STATE'],
    availability_status=SUBCLOUD_DICT['AVAILABILITY_STATUS'],
    management_subnet=SUBCLOUD_DICT['MANAGEMENT_SUBNET'],
    management_start_ip=SUBCLOUD_DICT['MANAGEMENT_START_IP'],
    management_end_ip=SUBCLOUD_DICT['MANAGEMENT_END_IP'],
    management_gateway_ip=SUBCLOUD_DICT['MANAGEMENT_GATEWAY_IP'],
    systemcontroller_gateway_ip=SUBCLOUD_DICT['SYSTEMCONTROLLER_GATEWAY_IP'],
    created_at=SUBCLOUD_DICT['CREATED_AT'],
    updated_at=SUBCLOUD_DICT['UPDATED_AT'])


class TestCLISubcloudManagerV1(base.BaseCommandTest):

    def test_list_subclouds(self):
        self.client.subcloud_manager.list_subclouds.return_value = [SUBCLOUD]
        actual_call = self.call(subcloud_cmd.ListSubcloud)
        self.assertEqual([(ID, NAME, MANAGEMENT_STATE, AVAILABILITY_STATUS,
                           "unknown")],
                         actual_call[1])

    def test_negative_list_subclouds(self):
        self.client.subcloud_manager.list_subclouds.return_value = []
        actual_call = self.call(subcloud_cmd.ListSubcloud)
        self.assertEqual((('<none>', '<none>', '<none>', '<none>',
                           '<none>'),),
                         actual_call[1])

    def test_delete_subcloud_with_subcloud_id(self):
        self.call(subcloud_cmd.DeleteSubcloud, app_args=[ID])
        self.client.subcloud_manager.delete_subcloud.\
            assert_called_once_with(ID)

    def test_delete_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.DeleteSubcloud, app_args=[])

    def test_show_subcloud_with_subcloud_id(self):
        self.client.subcloud_manager.subcloud_detail.\
            return_value = [SUBCLOUD]
        actual_call = self.call(subcloud_cmd.ShowSubcloud, app_args=[ID])
        self.assertEqual((ID, NAME,
                          DESCRIPTION,
                          LOCATION,
                          SOFTWARE_VERSION,
                          MANAGEMENT_STATE,
                          AVAILABILITY_STATUS,
                          MANAGEMENT_SUBNET,
                          MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP,
                          MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          TIME_NOW, TIME_NOW),
                         actual_call[1])

    def test_show_subcloud_negative(self):
        self.client.subcloud_manager.subcloud_detail.return_value = []
        actual_call = self.call(subcloud_cmd.ShowSubcloud, app_args=[ID])
        self.assertEqual((('<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>'),),
                         actual_call[1])

    def test_add_subcloud(self):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [SUBCLOUD]
        actual_call = self.call(
            subcloud_cmd.AddSubcloud, app_args=[
                '--name', NAME,
                '--description', DESCRIPTION,
                '--location', LOCATION,
                '--management-subnet', MANAGEMENT_SUBNET,
                '--management-start-ip', MANAGEMENT_START_IP,
                '--management-end-ip', MANAGEMENT_END_IP,
                '--management-gateway-ip', MANAGEMENT_GATEWAY_IP,
                '--systemcontroller-gateway-ip', SYSTEMCONTROLLER_GATEWAY_IP])
        self.assertEqual((ID, NAME, DESCRIPTION, LOCATION, SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          TIME_NOW, TIME_NOW), actual_call[1])

    def test_add_subcloud_no_optional_parameters(self):
        subcloud = copy.copy(SUBCLOUD)
        subcloud.description = ''
        subcloud.location = ''
        self.client.subcloud_manager.add_subcloud.\
            return_value = [subcloud]
        actual_call = self.call(
            subcloud_cmd.AddSubcloud, app_args=[
                '--name', NAME,
                '--management-subnet', MANAGEMENT_SUBNET,
                '--management-start-ip', MANAGEMENT_START_IP,
                '--management-end-ip', MANAGEMENT_END_IP,
                '--management-gateway-ip', MANAGEMENT_GATEWAY_IP,
                '--systemcontroller-gateway-ip', SYSTEMCONTROLLER_GATEWAY_IP])
        self.assertEqual((ID, NAME, '', '', SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          TIME_NOW, TIME_NOW), actual_call[1])

    def test_add_subcloud_without_name(self):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [SUBCLOUD]
        self.assertRaises(
            SystemExit, self.call, subcloud_cmd.AddSubcloud, app_args=[
                '--description', DESCRIPTION,
                '--location', LOCATION,
                '--management-subnet', MANAGEMENT_SUBNET,
                '--management-start-ip', MANAGEMENT_START_IP,
                '--management-end-ip', MANAGEMENT_END_IP,
                '--management-gateway-ip', MANAGEMENT_GATEWAY_IP,
                '--systemcontroller-gateway-ip', SYSTEMCONTROLLER_GATEWAY_IP])

    def test_unmanage_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [SUBCLOUD]
        actual_call = self.call(
            subcloud_cmd.UnmanageSubcloud, app_args=[ID])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          TIME_NOW, TIME_NOW), actual_call[1])

    def test_unmanage_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.UnmanageSubcloud, app_args=[])

    def test_manage_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [SUBCLOUD]
        actual_call = self.call(
            subcloud_cmd.ManageSubcloud, app_args=[ID])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          TIME_NOW, TIME_NOW), actual_call[1])

    def test_manage_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.ManageSubcloud, app_args=[])

    def test_update_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [SUBCLOUD]
        actual_call = self.call(
            subcloud_cmd.UpdateSubcloud,
            app_args=[ID,
                      '--description', 'subcloud description',
                      '--location', 'subcloud location'])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          TIME_NOW, TIME_NOW), actual_call[1])

    def test_generate_config_subcloud(self):
        FAKE_CONFIG = "This is a fake config file."
        self.client.subcloud_manager.generate_config_subcloud.\
            return_value = FAKE_CONFIG
        actual_call = self.call(
            subcloud_cmd.GenerateConfigSubcloud, app_args=[ID])
        self.assertEqual(FAKE_CONFIG, actual_call)

    def test_generate_config_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.GenerateConfigSubcloud, app_args=[])
