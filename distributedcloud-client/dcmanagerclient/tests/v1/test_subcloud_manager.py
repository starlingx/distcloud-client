# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2023 Wind River Systems, Inc.
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

import copy
import mock
import os
import tempfile
import yaml

from dcmanagerclient.commands.v1 import subcloud_manager as subcloud_cmd
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base


class TestCLISubcloudManagerV1(base.BaseCommandTest):

    def test_list_subclouds(self):
        self.client.subcloud_manager.list_subclouds.return_value = \
            [base.SUBCLOUD_RESOURCE]
        actual_call = self.call(subcloud_cmd.ListSubcloud)
        self.assertEqual([base.SUBCLOUD_LIST_RESULT],
                         actual_call[1])

    def test_negative_list_subclouds(self):
        self.client.subcloud_manager.list_subclouds.return_value = []
        actual_call = self.call(subcloud_cmd.ListSubcloud)
        self.assertEqual(base.EMPTY_SUBCLOUD_LIST_RESULT,
                         actual_call[1])

    def test_delete_subcloud_with_subcloud_id(self):
        self.call(subcloud_cmd.DeleteSubcloud, app_args=[base.ID])
        self.client.subcloud_manager.delete_subcloud.\
            assert_called_once_with(base.ID)

    def test_delete_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.DeleteSubcloud, app_args=[])

    def test_show_subcloud_with_subcloud_id(self):
        self.client.subcloud_manager.subcloud_detail.\
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call = self.call(subcloud_cmd.ShowSubcloud, app_args=[base.ID])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    def test_show_subcloud_with_additional_detail(self):
        SUBCLOUD_WITH_ADDITIONAL_DETAIL = copy.copy(base.SUBCLOUD_RESOURCE)
        SUBCLOUD_WITH_ADDITIONAL_DETAIL.oam_floating_ip = \
            base.EXTERNAL_OAM_FLOATING_ADDRESS
        SUBCLOUD_WITH_ADDITIONAL_DETAIL.deploy_config_sync_status =  \
            base.DEPLOY_CONFIG_SYNC_STATUS
        SUBCLOUD_WITH_ADDITIONAL_DETAIL.region_name = \
            base.REGION_NAME
        self.client.subcloud_manager.subcloud_additional_details.\
            return_value = [SUBCLOUD_WITH_ADDITIONAL_DETAIL]
        actual_call = self.call(subcloud_cmd.ShowSubcloud,
                                app_args=[base.ID, '--detail'])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID +
            (base.EXTERNAL_OAM_FLOATING_ADDRESS,
             base.DEPLOY_CONFIG_SYNC_STATUS, base.REGION_NAME),
            actual_call[1])

    def test_show_subcloud_negative(self):
        self.client.subcloud_manager.subcloud_detail.return_value = []
        actual_call = self.call(subcloud_cmd.ShowSubcloud, app_args=[base.ID])
        self.assertEqual(
            base.EMPTY_SUBCLOUD_FIELD_RESULT_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_add_subcloud(self, getpass):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(base.FAKE_BOOTSTRAP_VALUES, f)
            file_path = os.path.abspath(f.name)
            # Without "--release" parameter
            actual_call1 = self.call(
                subcloud_cmd.AddSubcloud, app_args=[
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', file_path,
                ])
            # With "--release" parameter
            actual_call2 = self.call(
                subcloud_cmd.AddSubcloud, app_args=[
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', file_path,
                    '--release', base.SOFTWARE_VERSION,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call1[1])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call2[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_add_migrate_subcloud(self, getpass):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(base.FAKE_BOOTSTRAP_VALUES, f)
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                subcloud_cmd.AddSubcloud, app_args=[
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', file_path,
                    '--migrate',
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_add_migrate_subcloud_with_deploy_config(self, getpass):
        self.client.subcloud_manager.add_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as f_bootstrap:
            bootstrap_file_path = os.path.abspath(f_bootstrap.name)

            with tempfile.NamedTemporaryFile() as f_config:
                config_file_path = os.path.abspath(f_config.name)

                self.assertRaises(
                    DCManagerClientException, self.call,
                    subcloud_cmd.AddSubcloud, app_args=[
                        '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                        '--bootstrap-values', bootstrap_file_path,
                        '--deploy-config', config_file_path,
                        '--migrate',
                    ])

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_add_migrate_subcloud_with_name_change(self, getpass):
        SUBCLOUD_RESOURCE = copy.\
            copy(base.SUBCLOUD_RESOURCE_WITH_PEERID)
        SUBCLOUD_RESOURCE.name = base.NAME_SC2
        self.client.subcloud_manager.add_subcloud.\
            return_value = [SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(base.FAKE_BOOTSTRAP_VALUES, f)
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                subcloud_cmd.AddSubcloud, app_args=[
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', file_path,
                    '--migrate',
                    '--name', base.NAME_SC2
                ])
        SUBCLOUD_FIELD_RESULT = base.\
            SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID
        RESULT_LIST = list(SUBCLOUD_FIELD_RESULT)
        RESULT_LIST[1] = base.NAME_SC2
        self.assertEqual(tuple(RESULT_LIST), actual_call[1])

    def test_rename_subcloud(self):
        SUBCLOUD_RENAMED = copy.\
            copy(base.SUBCLOUD_RESOURCE_WITH_PEERID)
        SUBCLOUD_RENAMED.name = base.NAME_SC2
        self.client.subcloud_manager.update_subcloud.\
            return_value = [SUBCLOUD_RENAMED]

        # Rename by id
        actual_call1 = self.call(
            subcloud_cmd.UpdateSubcloud,
            app_args=[base.ID, '--name', base.NAME_SC2])
        results_by_id = \
            list(base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID)
        results_by_id[1] = base.NAME_SC2

        # Rename by name
        actual_call2 = self.call(
            subcloud_cmd.UpdateSubcloud,
            app_args=[base.NAME, '--name', base.NAME_SC2])

        SUBCLOUD_FIELD_RESULT = base.\
            SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID
        results_by_name = list(SUBCLOUD_FIELD_RESULT)
        results_by_name[1] = base.NAME_SC2

        self.assertEqual(tuple(results_by_id), actual_call1[1])
        self.assertEqual(tuple(results_by_name), actual_call2[1])

    def test_update_fields_values(self):
        SUBCLOUD_WITH_REGION_DETAIL = copy.copy(base.SUBCLOUD_RESOURCE)
        SUBCLOUD_WITH_REGION_DETAIL.region_name = base.REGION_NAME

        SUBCLOUD_WITH_REGION_NONE = copy.copy(base.SUBCLOUD_RESOURCE)
        SUBCLOUD_WITH_REGION_NONE.region_name = None

        subcloud_cmd.update_fields_values([SUBCLOUD_WITH_REGION_DETAIL])

        self.assertEqual(SUBCLOUD_WITH_REGION_DETAIL.region_name,
                         SUBCLOUD_WITH_REGION_NONE.region_name)

    def test_unmanage_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call = self.call(
            subcloud_cmd.UnmanageSubcloud, app_args=[base.ID])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    def test_unmanage_subcloud_with_migrate(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call = self.call(
            subcloud_cmd.UnmanageSubcloud, app_args=[base.ID, '--migrate'])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    def test_unmanage_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.UnmanageSubcloud, app_args=[])

    def test_manage_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call = self.call(
            subcloud_cmd.ManageSubcloud, app_args=[base.ID])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    def test_manage_subcloud_without_subcloud_id(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.ManageSubcloud, app_args=[])

    def test_update_subcloud(self):
        self.client.subcloud_manager.update_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        with tempfile.NamedTemporaryFile(mode='w') as f_bootstrap:
            bootstrap_file_path = os.path.abspath(f_bootstrap.name)
            actual_call = self.call(
                subcloud_cmd.UpdateSubcloud,
                app_args=[
                    base.ID,
                    '--description', 'subcloud description',
                    '--location', 'subcloud location',
                    '--sysadmin-password', 'testpassword',
                    '--management-subnet', 'subcloud network subnet',
                    '--management-gateway-ip', 'subcloud network gateway ip',
                    '--management-start-ip', 'sc network start ip',
                    '--management-end-ip', 'subcloud network end ip',
                    '--bootstrap-address', 'subcloud bootstrap address',
                    '--bootstrap-values', bootstrap_file_path,
                    '--peer-group', 'peer group'])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    @mock.patch('six.moves.input', return_value='redeploy')
    def test_redeploy_subcloud(self, mock_input, getpass):
        self.client.subcloud_manager.redeploy_subcloud. \
            return_value = [base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as bootstrap_file,\
            tempfile.NamedTemporaryFile(mode='w') as config_file,\
            tempfile.NamedTemporaryFile(mode='w') as install_file:

            bootstrap_file_path = os.path.abspath(bootstrap_file.name)
            config_file_path = os.path.abspath(config_file.name)
            install_file_path = os.path.abspath(install_file.name)

            actual_call = self.call(
                subcloud_cmd.RedeploySubcloud, app_args=[
                    base.NAME,
                    '--bootstrap-values', bootstrap_file_path,
                    '--install-values', install_file_path,
                    '--deploy-config', config_file_path,
                    '--release', base.SOFTWARE_VERSION,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    @mock.patch('six.moves.input', return_value='redeploy')
    def test_redeploy_subcloud_no_parameters(self, mock_input, getpass):
        self.client.subcloud_manager.redeploy_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call = self.call(
            subcloud_cmd.RedeploySubcloud,
            app_args=[base.ID])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call[1])

    @mock.patch('getpass.getpass', return_value='testpassword')
    @mock.patch('six.moves.input', return_value='redeploy')
    def test_redeploy_bootstrap_files_does_not_exists(
        self, mock_input, getpass):
        self.client.subcloud_manager.redeploy_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        with tempfile.NamedTemporaryFile(mode='w') as bootstrap_file,\
            tempfile.NamedTemporaryFile(mode='w') as config_file,\
            tempfile.NamedTemporaryFile(mode='w') as install_file:

            bootstrap_file_path = os.path.abspath(bootstrap_file.name)
            config_file_path = os.path.abspath(config_file.name)
            install_file_path = os.path.abspath(install_file.name)

        app_args_install = [base.NAME,
                            '--install-values', install_file_path]
        app_args_bootstrap = [base.NAME,
                              '--bootstrap-values', bootstrap_file_path]
        app_args_config = [base.NAME, '--deploy-config', config_file_path]
        args_dict = {'install-values': app_args_install,
                     'bootstrap-values': app_args_bootstrap,
                     'deploy-config': app_args_config}

        for file in ['install-values', 'bootstrap-values',
                     'deploy-config']:
            e = self.assertRaises(DCManagerClientException,
                                  self.call,
                                  subcloud_cmd.RedeploySubcloud,
                                  app_args=args_dict[file])
            self.assertTrue(f'{file} does not exist' in str(e))

    @mock.patch('getpass.getpass', return_value='testpassword')
    def test_restore_subcloud(self, getpass):
        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)

            e = self.assertRaises(DCManagerClientException,
                                  self.call,
                                  subcloud_cmd.RestoreSubcloud,
                                  app_args=[base.ID,
                                            '--restore-values',
                                            file_path])

            deprecation_msg = ('This command has been deprecated. Please use '
                               'subcloud-backup restore instead.')
            self.assertTrue(deprecation_msg in str(e))

    def test_prestage_with_subcloudID(self):
        self.client.subcloud_manager.prestage_subcloud.\
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call_without_release = self.call(
            subcloud_cmd.PrestageSubcloud,
            app_args=[base.ID,
                      '--sysadmin-password', 'testpassword',
                      '--force'])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call_without_release[1])

    def test_prestage_without_subcloudID(self):
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.PrestageSubcloud, app_args=[])

    def test_prestage_with_release(self):
        SUBCLOUD_WITH_ADDITIONAL_DETAIL = copy.copy(base.SUBCLOUD_RESOURCE)
        SUBCLOUD_WITH_ADDITIONAL_DETAIL.prestage_software_version = \
            base.SOFTWARE_VERSION
        self.client.subcloud_manager.prestage_subcloud.return_value = \
            [SUBCLOUD_WITH_ADDITIONAL_DETAIL]
        actual_call_with_release = self.call(
            subcloud_cmd.PrestageSubcloud,
            app_args=[base.ID,
                      '--sysadmin-password', 'testpassword',
                      '--force',
                      '--release', base.SOFTWARE_VERSION])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID +
            (base.SOFTWARE_VERSION,),
            actual_call_with_release[1])

    def test_migrate_subcloud(self):
        self.client.subcloud_manager.migrate_subcloud. \
            return_value = [base.SUBCLOUD_RESOURCE]
        actual_call_without_release = self.call(
            subcloud_cmd.MigrateSubcloud,
            app_args=[base.ID,
                      '--sysadmin-password', 'testpassword'])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID,
            actual_call_without_release[1])
        self.assertRaises(SystemExit, self.call,
                          subcloud_cmd.MigrateSubcloud, app_args=[])
