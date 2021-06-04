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
# Copyright (c) 2017-2021 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import copy
import mock
import os
import tempfile
import yaml

from oslo_utils import timeutils

from dcmanagerclient.api.v1 import subcloud_manager as sm
from dcmanagerclient.commands.v1 import subcloud_manager as subcloud_cmd
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base

BOOTSTRAP_ADDRESS = '10.10.10.12'
TIME_NOW = timeutils.utcnow().isoformat()
ID = '1'
ID_1 = '2'
NAME = 'subcloud1'
SYSTEM_MODE = "duplex"
DESCRIPTION = 'subcloud1 description'
LOCATION = 'subcloud1 location'
SOFTWARE_VERSION = '12.34'
MANAGEMENT_STATE = 'unmanaged'
AVAILABILITY_STATUS = 'offline'
DEPLOY_STATUS = 'not-deployed'
DEPLOY_STATE_PRE_DEPLOY = 'pre-deploy'
DEPLOY_STATE_PRE_RESTORE = 'pre-restore'
MANAGEMENT_SUBNET = '192.168.101.0/24'
MANAGEMENT_START_IP = '192.168.101.2'
MANAGEMENT_END_IP = '192.168.101.50'
MANAGEMENT_GATEWAY_IP = '192.168.101.1'
SYSTEMCONTROLLER_GATEWAY_IP = '192.168.204.101'
EXTERNAL_OAM_SUBNET = "10.10.10.0/24"
EXTERNAL_OAM_GATEWAY_ADDRESS = "10.10.10.1"
EXTERNAL_OAM_FLOATING_ADDRESS = "10.10.10.12"
DEFAULT_SUBCLOUD_GROUP_ID = '1'

SUBCLOUD_DICT = {
    'SUBCLOUD_ID': ID,
    'NAME': NAME,
    'DESCRIPTION': DESCRIPTION,
    'LOCATION': LOCATION,
    'SOFTWARE_VERSION': SOFTWARE_VERSION,
    'MANAGEMENT_STATE': MANAGEMENT_STATE,
    'AVAILABILITY_STATUS': AVAILABILITY_STATUS,
    'DEPLOY_STATUS': DEPLOY_STATUS,
    'MANAGEMENT_SUBNET': MANAGEMENT_SUBNET,
    'MANAGEMENT_START_IP': MANAGEMENT_START_IP,
    'MANAGEMENT_END_IP': MANAGEMENT_END_IP,
    'MANAGEMENT_GATEWAY_IP': MANAGEMENT_GATEWAY_IP,
    'SYSTEMCONTROLLER_GATEWAY_IP': SYSTEMCONTROLLER_GATEWAY_IP,
    'CREATED_AT': TIME_NOW,
    'UPDATED_AT': TIME_NOW,
    'GROUP_ID': DEFAULT_SUBCLOUD_GROUP_ID,
    'OAM_FLOATING_IP': EXTERNAL_OAM_FLOATING_ADDRESS
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
    deploy_status=SUBCLOUD_DICT['DEPLOY_STATUS'],
    management_subnet=SUBCLOUD_DICT['MANAGEMENT_SUBNET'],
    management_start_ip=SUBCLOUD_DICT['MANAGEMENT_START_IP'],
    management_end_ip=SUBCLOUD_DICT['MANAGEMENT_END_IP'],
    management_gateway_ip=SUBCLOUD_DICT['MANAGEMENT_GATEWAY_IP'],
    systemcontroller_gateway_ip=SUBCLOUD_DICT['SYSTEMCONTROLLER_GATEWAY_IP'],
    created_at=SUBCLOUD_DICT['CREATED_AT'],
    updated_at=SUBCLOUD_DICT['UPDATED_AT'],
    group_id=SUBCLOUD_DICT['GROUP_ID'])

DEFAULT_SUBCLOUD_FIELD_RESULT_LIST = (
    ID,
    NAME,
    DESCRIPTION,
    LOCATION,
    SOFTWARE_VERSION,
    MANAGEMENT_STATE,
    AVAILABILITY_STATUS,
    DEPLOY_STATUS,
    MANAGEMENT_SUBNET,
    MANAGEMENT_START_IP,
    MANAGEMENT_END_IP,
    MANAGEMENT_GATEWAY_IP,
    SYSTEMCONTROLLER_GATEWAY_IP,
    DEFAULT_SUBCLOUD_GROUP_ID,
    TIME_NOW,
    TIME_NOW)


class TestCLISubcloudManagerV1(base.BaseCommandTest):

    def test_list_subclouds(self):
        self.client.subcloud_manager.list_subclouds.return_value = [SUBCLOUD]
        actual_call = self.call(subcloud_cmd.ListSubcloud)
        self.assertEqual([(ID, NAME, MANAGEMENT_STATE, AVAILABILITY_STATUS,
                           DEPLOY_STATUS, "unknown")],
                         actual_call[1])

    def test_negative_list_subclouds(self):
        self.client.subcloud_manager.list_subclouds.return_value = []
        actual_call = self.call(subcloud_cmd.ListSubcloud)
        self.assertEqual((('<none>', '<none>', '<none>', '<none>', '<none>',
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
        self.assertEqual(DEFAULT_SUBCLOUD_FIELD_RESULT_LIST,
                         actual_call[1])

    def test_show_subcloud_with_additional_detail(self):
        SUBCLOUD_WITH_ADDITIONAL_DETAIL = copy.copy(SUBCLOUD)
        SUBCLOUD_WITH_ADDITIONAL_DETAIL.oam_floating_ip =  \
            SUBCLOUD_DICT['OAM_FLOATING_IP']
        self.client.subcloud_manager.subcloud_additional_details.\
            return_value = [SUBCLOUD_WITH_ADDITIONAL_DETAIL]
        actual_call = self.call(subcloud_cmd.ShowSubcloud,
                                app_args=[ID, '--detail'])
        self.assertEqual((ID, NAME,
                          DESCRIPTION,
                          LOCATION,
                          SOFTWARE_VERSION,
                          MANAGEMENT_STATE,
                          AVAILABILITY_STATUS,
                          DEPLOY_STATUS,
                          MANAGEMENT_SUBNET,
                          MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP,
                          MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW,
                          EXTERNAL_OAM_FLOATING_ADDRESS),
                         actual_call[1])

    def test_show_subcloud_negative(self):
        self.client.subcloud_manager.subcloud_detail.return_value = []
        actual_call = self.call(subcloud_cmd.ShowSubcloud, app_args=[ID])
        self.assertEqual((('<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>', '<none>', '<none>',
                           '<none>', '<none>', '<none>', '<none>'),),
                         actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_add_subcloud(self, getpass):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [SUBCLOUD]

        values = {
            "system_mode": SYSTEM_MODE,
            "name": NAME,
            "description": DESCRIPTION,
            "location": LOCATION,
            "management_subnet": MANAGEMENT_SUBNET,
            "management_start_address": MANAGEMENT_START_IP,
            "management_end_address": MANAGEMENT_END_IP,
            "management_gateway_address": MANAGEMENT_GATEWAY_IP,
            "external_oam_subnet": EXTERNAL_OAM_SUBNET,
            "external_oam_gateway_address": EXTERNAL_OAM_GATEWAY_ADDRESS,
            "external_oam_floating_address": EXTERNAL_OAM_FLOATING_ADDRESS,
        }

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(values, f)
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                subcloud_cmd.AddSubcloud, app_args=[
                    '--bootstrap-address', BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', file_path,
                ])
        self.assertEqual((ID, NAME, DESCRIPTION, LOCATION, SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS, DEPLOY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW), actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_add_migrate_subcloud(self, getpass):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [SUBCLOUD]

        values = {
            "system_mode": SYSTEM_MODE,
            "name": NAME,
            "description": DESCRIPTION,
            "location": LOCATION,
            "management_subnet": MANAGEMENT_SUBNET,
            "management_start_address": MANAGEMENT_START_IP,
            "management_end_address": MANAGEMENT_END_IP,
            "management_gateway_address": MANAGEMENT_GATEWAY_IP,
            "external_oam_subnet": EXTERNAL_OAM_SUBNET,
            "external_oam_gateway_address": EXTERNAL_OAM_GATEWAY_ADDRESS,
            "external_oam_floating_address": EXTERNAL_OAM_FLOATING_ADDRESS,
        }

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(values, f)
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                subcloud_cmd.AddSubcloud, app_args=[
                    '--bootstrap-address', BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', file_path,
                    '--migrate',
                ])
        self.assertEqual((ID, NAME, DESCRIPTION, LOCATION, SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS, DEPLOY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW), actual_call[1])

    def test_unmanage_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [SUBCLOUD]
        actual_call = self.call(
            subcloud_cmd.UnmanageSubcloud, app_args=[ID])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS, DEPLOY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
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
                          AVAILABILITY_STATUS, DEPLOY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
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
                          AVAILABILITY_STATUS, DEPLOY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW), actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_success_reconfigure_subcloud(self, getpass):
        SUBCLOUD_BEING_DEPLOYED = copy.copy(SUBCLOUD)
        SUBCLOUD_BEING_DEPLOYED.deploy_status = DEPLOY_STATE_PRE_DEPLOY
        self.client.subcloud_manager.reconfigure_subcloud.\
            return_value = [SUBCLOUD_BEING_DEPLOYED]

        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                subcloud_cmd.ReconfigSubcloud,
                app_args=[ID,
                          '--deploy-config', file_path])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS, DEPLOY_STATE_PRE_DEPLOY,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW), actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_reconfigure_file_does_not_exist(self, getpass):
        SUBCLOUD_BEING_DEPLOYED = copy.copy(SUBCLOUD)
        SUBCLOUD_BEING_DEPLOYED.deploy_status = DEPLOY_STATE_PRE_DEPLOY
        self.client.subcloud_manager.reconfigure_subcloud.\
            return_value = [SUBCLOUD_BEING_DEPLOYED]

        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_cmd.ReconfigSubcloud,
                              app_args=[ID, '--deploy-config', file_path])
        self.assertTrue('deploy-config file does not exist'
                        in str(e))

    @mock.patch('six.moves.input', return_value='reinstall')
    def test_reinstall_subcloud(self, mock_input):
        self.client.subcloud_manager.reinstall_subcloud.\
            return_value = [SUBCLOUD]
        actual_call = self.call(
            subcloud_cmd.ReinstallSubcloud, app_args=[ID])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS, DEPLOY_STATUS,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW), actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_restore_subcloud(self, getpass):
        self.client.subcloud_manager.subcloud_detail.\
            return_value = [SUBCLOUD]

        SUBCLOUD_BEING_RESTORED = copy.copy(SUBCLOUD)
        setattr(SUBCLOUD_BEING_RESTORED,
                'deploy_status',
                DEPLOY_STATE_PRE_RESTORE)

        self.client.subcloud_manager.restore_subcloud.\
            return_value = [SUBCLOUD_BEING_RESTORED]

        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                subcloud_cmd.RestoreSubcloud,
                app_args=[ID,
                          '--restore-values', file_path])
        self.assertEqual((ID, NAME,
                          DESCRIPTION, LOCATION,
                          SOFTWARE_VERSION, MANAGEMENT_STATE,
                          AVAILABILITY_STATUS, DEPLOY_STATE_PRE_RESTORE,
                          MANAGEMENT_SUBNET, MANAGEMENT_START_IP,
                          MANAGEMENT_END_IP, MANAGEMENT_GATEWAY_IP,
                          SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW), actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_restore_file_does_not_exist(self, getpass):
        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_cmd.RestoreSubcloud,
                              app_args=[ID, '--restore-values', file_path])
        self.assertTrue('restore-values does not exist'
                        in str(e))

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_restore_subcloud_does_not_exist(self, getpass):
        self.client.subcloud_manager.subcloud_detail.\
            return_value = []

        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_cmd.RestoreSubcloud,
                              app_args=[ID, '--restore-values', file_path])
        self.assertTrue('does not exist'
                        in str(e))
