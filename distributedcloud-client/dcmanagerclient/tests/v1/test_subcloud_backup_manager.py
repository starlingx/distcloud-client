#
# Copyright (c) 2022 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64
import mock
import os

from oslo_utils import timeutils

from dcmanagerclient.api import base as api_base
from dcmanagerclient.commands.v1 \
    import subcloud_backup_manager as subcloud_backup_cmd
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
ERROR_DESCRIPTION = 'test error description'
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
BACKUP_VALUES = """---
                platform_backup_filename_prefix: test
                openstack_app_name: test
                backup_dir: test
                host_backup_dir: test
                """

SUBCLOUD_DICT = {
    'SUBCLOUD_ID': ID,
    'NAME': NAME,
    'DESCRIPTION': DESCRIPTION,
    'LOCATION': LOCATION,
    'SOFTWARE_VERSION': SOFTWARE_VERSION,
    'MANAGEMENT_STATE': MANAGEMENT_STATE,
    'AVAILABILITY_STATUS': AVAILABILITY_STATUS,
    'DEPLOY_STATUS': DEPLOY_STATUS,
    'ERROR_DESCRIPTION': ERROR_DESCRIPTION,
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

SUBCLOUD = api_base.Subcloud(
    mock,
    subcloud_id=SUBCLOUD_DICT['SUBCLOUD_ID'],
    name=SUBCLOUD_DICT['NAME'],
    description=SUBCLOUD_DICT['DESCRIPTION'],
    location=SUBCLOUD_DICT['LOCATION'],
    software_version=SUBCLOUD_DICT['SOFTWARE_VERSION'],
    management_state=SUBCLOUD_DICT['MANAGEMENT_STATE'],
    availability_status=SUBCLOUD_DICT['AVAILABILITY_STATUS'],
    deploy_status=SUBCLOUD_DICT['DEPLOY_STATUS'],
    error_description=SUBCLOUD_DICT['ERROR_DESCRIPTION'],
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


class TestCLISubcloudBackUpManagerV1(base.BaseCommandTest):

    def setUp(self):
        super(TestCLISubcloudBackUpManagerV1, self).setUp()
        self.client = self.app.client_manager.subcloud_backup_manager

    def test_backup_create_subcloud(self):

        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = [SUBCLOUD]

        backupPath = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backupPath, mode='w') as f:
            f.write(BACKUP_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=['--subcloud', 'subcloud1',
                      '--local-only',
                      '--registry-images',
                      '--backup-values', backupPath,
                      '--sysadmin-password', 'testpassword'])
        self.assertEqual([(ID, NAME, DESCRIPTION, LOCATION, SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS, DEPLOY_STATUS,
                          ERROR_DESCRIPTION, MANAGEMENT_SUBNET,
                          MANAGEMENT_START_IP, MANAGEMENT_END_IP,
                          MANAGEMENT_GATEWAY_IP, SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW, None, None)], actual_call[1])

    def test_backup_create_group(self):

        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = [SUBCLOUD]

        backupPath = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backupPath, mode='w') as f:
            f.write(BACKUP_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=['--group', 'test',
                      '--backup-values', backupPath,
                      '--sysadmin-password', 'testpassword'])
        self.assertEqual([(ID, NAME, DESCRIPTION, LOCATION, SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS, DEPLOY_STATUS,
                          ERROR_DESCRIPTION, MANAGEMENT_SUBNET,
                          MANAGEMENT_START_IP, MANAGEMENT_END_IP,
                          MANAGEMENT_GATEWAY_IP, SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW, None, None)], actual_call[1])

    def test_backup_create_group_subcloud(self):
        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = []

        backupPath = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backupPath, mode='w') as f:
            f.write(BACKUP_VALUES)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_backup_cmd.CreateSubcloudBackup,
                              app_args=['--subcloud', 'subcloud1',
                                        '--group', 'test',
                                        '--local-only',
                                        '--backup-values', backupPath,
                                        '--sysadmin-password', 'testpassword'])
        self.assertTrue(('The command only applies to a single subcloud or a'
                        ' subcloud group, not both.') in str(e))

    def test_backup_create_no_group_no_subcloud(self):
        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = []

        backupPath = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backupPath, mode='w') as f:
            f.write(BACKUP_VALUES)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_backup_cmd.CreateSubcloudBackup,
                              app_args=['--local-only',
                                        '--backup-values', backupPath,
                                        '--sysadmin-password', 'testpassword'])

        self.assertTrue(('Please provide the subcloud or subcloud group name'
                        ' or id.') in str(e))

    def test_backup_create_backup_value_not_a_file(self):
        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = []

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_backup_cmd.CreateSubcloudBackup,
                              app_args=['--subcloud', 'subcloud1',
                                        '--local-only',
                                        '--backup-values', 'notADirectory',
                                        '--sysadmin-password', 'testpassword'])

        self.assertTrue('Backup-values file does not exist' in str(e))

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_backup_create_prompt_ask_for_password(self, getpass):

        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = [SUBCLOUD]

        backupPath = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backupPath, mode='w') as f:
            f.write(BACKUP_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=['--group', 'test',
                      '--local-only',
                      '--backup-values', backupPath])
        self.assertEqual([(ID, NAME, DESCRIPTION, LOCATION, SOFTWARE_VERSION,
                          MANAGEMENT_STATE, AVAILABILITY_STATUS, DEPLOY_STATUS,
                          ERROR_DESCRIPTION, MANAGEMENT_SUBNET,
                          MANAGEMENT_START_IP, MANAGEMENT_END_IP,
                          MANAGEMENT_GATEWAY_IP, SYSTEMCONTROLLER_GATEWAY_IP,
                          DEFAULT_SUBCLOUD_GROUP_ID,
                          TIME_NOW, TIME_NOW, None, None)], actual_call[1])

    def test_backup_create_local_only_registry_images(self):

        self.client.subcloud_backup_manager.backup_subcloud_create.\
            return_value = []

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_backup_cmd.CreateSubcloudBackup,
                              app_args=['--subcloud', 'subcloud1',
                                        '--registry-images',
                                        '--backup-values', 'notADirectory',
                                        '--sysadmin-password', 'testpassword'])

        self.assertTrue(('Option --registry-images can not be used without '
                         '--local-only option.') in str(e))

    def test_backup_delete_no_group_no_subcloud(self):
        self.client.subcloud_backup_manager.backup_subcloud_delete.\
            return_value = []

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_backup_cmd.DeleteSubcloudBackup,
                              app_args=['release',
                                        '--local-only',
                                        '--sysadmin-password', 'testpassword'])

        self.assertTrue(('Please provide the subcloud or subcloud group'
                         ' name or id.') in str(e))

    def test_backup_delete_group_subcloud(self):
        self.client.subcloud_backup_manager.backup_subcloud_delete.\
            return_value = []

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              subcloud_backup_cmd.DeleteSubcloudBackup,
                              app_args=['release',
                                        '--subcloud', 'subcloud1',
                                        '--group', 'group1',
                                        '--local-only',
                                        '--sysadmin-password', 'testpassword'])

        self.assertTrue(('This command only applies to a single subcloud '
                         'or a subcloud group, not both.') in str(e))

    def test_backup_delete_group(self):

        groupName = 'test_group_1'
        releaseVersion = 'release_version_2'
        password = 'testpassword'
        encodedPassword = base64.b64encode(password.encode("utf-8")).\
            decode("utf-8")

        payload = {'release': releaseVersion, 'group': groupName,
                   'local_only': 'true', 'sysadmin_password': encodedPassword}

        app_args = [releaseVersion,
                    '--group', groupName,
                    '--local-only',
                    '--sysadmin-password', password]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.subcloud_backup_manager.backup_subcloud_delete.\
            assert_called_once_with(data=payload,
                                    release_version=releaseVersion,
                                    subcloud_ref=None)

    def test_backup_delete_subcloud(self):

        subcloudName = 'subcloud1'
        releaseVersion = 'release_version_2'
        password = 'testpassword'
        encodedPassword = base64.b64encode(password.encode("utf-8")).\
            decode("utf-8")

        payload = {'release': releaseVersion, 'subcloud': subcloudName,
                   'local_only': 'true', 'sysadmin_password': encodedPassword}

        app_args = [releaseVersion,
                    '--subcloud', subcloudName,
                    '--local-only',
                    '--sysadmin-password', password]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.subcloud_backup_manager.backup_subcloud_delete.\
            assert_called_once_with(data=payload,
                                    release_version=releaseVersion,
                                    subcloud_ref=subcloudName)

    def test_backup_delete_no_local_only(self):

        groupName = 'test_group_1'
        releaseVersion = 'release_version_2'
        password = 'testpassword'
        encodedPassword = base64.b64encode(password.encode("utf-8")).\
            decode("utf-8")

        payload = {'release': releaseVersion, 'group': groupName,
                   'local_only': 'false', 'sysadmin_password': encodedPassword}

        app_args = [releaseVersion,
                    '--group', groupName,
                    '--sysadmin-password', password]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.subcloud_backup_manager.backup_subcloud_delete.\
            assert_called_once_with(data=payload,
                                    release_version=releaseVersion,
                                    subcloud_ref=None)

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_backup_delete_prompt_ask_for_password(self, getpass):

        groupName = 'test_group_1'
        releaseVersion = 'release_version_2'
        password = 'testpassword'
        encodedPassword = base64.b64encode(password.encode("utf-8")).\
            decode("utf-8")

        payload = {'release': releaseVersion, 'group': groupName,
                   'local_only': 'true', 'sysadmin_password': encodedPassword}

        app_args = [releaseVersion,
                    '--group', groupName,
                    '--local-only']

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.subcloud_backup_manager.backup_subcloud_delete.\
            assert_called_once_with(data=payload,
                                    release_version=releaseVersion,
                                    subcloud_ref=None)

    def test_backup_delete_subcloud_no_release_version(self):

        subcloudName = 'subcloud1'
        password = 'testpassword'

        app_args = ['--subcloud', subcloudName,
                    '--local-only',
                    '--sysadmin-password', password]

        self.assertRaises(SystemExit, self.call,
                          subcloud_backup_cmd.DeleteSubcloudBackup,
                          app_args=app_args)
