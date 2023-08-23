#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import os
import tempfile

import mock
import yaml

from dcmanagerclient.commands.v1 import phased_subcloud_deploy_manager as cmd
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base


@mock.patch('getpass.getpass', new=mock.Mock(return_value='testpassword'))
class TestCLIPhasedSubcloudDeployManagerV1(base.BaseCommandTest):

    def setUp(self):
        super().setUp()
        # The client is the subcloud_deploy_manager
        self.client = self.app.client_manager.phased_subcloud_deploy_manager.\
            phased_subcloud_deploy_manager

    def test_subcloud_deploy_create(self):
        self.client.subcloud_deploy_create.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as bootstrap_file,\
            tempfile.NamedTemporaryFile(mode='w') as config_file,\
            tempfile.NamedTemporaryFile(mode='w') as install_file:

            bootstrap_file_path = os.path.abspath(bootstrap_file.name)
            config_file_path = os.path.abspath(config_file.name)
            install_file_path = os.path.abspath(install_file.name)

            actual_call = self.call(
                cmd.CreatePhasedSubcloudDeploy, app_args=[
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--install-values', install_file_path,
                    '--bootstrap-values', bootstrap_file_path,
                    '--deploy-config', config_file_path,
                    '--release', base.SOFTWARE_VERSION,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_subcloud_deploy_bootstrap(self):
        self.client.subcloud_deploy_bootstrap.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as bootstrap_file:
            bootstrap_file_path = os.path.abspath(bootstrap_file.name)

            actual_call = self.call(
                cmd.BootstrapPhasedSubcloudDeploy, app_args=[
                    base.ID,
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', bootstrap_file_path,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_install_subcloud(self):
        self.client.subcloud_deploy_install.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(base.FAKE_INSTALL_VALUES, f)
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                cmd.InstallPhasedSubcloudDeploy, app_args=[
                    base.NAME, '--install-values', file_path,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_install_subcloud_with_release(self):
        self.client.subcloud_deploy_install.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as f:
            yaml.dump(base.FAKE_INSTALL_VALUES, f)
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                cmd.InstallPhasedSubcloudDeploy, app_args=[
                    base.NAME,
                    '--install-values', file_path,
                    '--release', base.SOFTWARE_VERSION,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_install_subcloud_without_install_values(self):
        self.client.subcloud_deploy_install.return_value = [
            base.SUBCLOUD_RESOURCE]

        actual_call = self.call(
            cmd.InstallPhasedSubcloudDeploy, app_args=[base.NAME])

        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_install_file_does_not_exist(self):
        self.client.subcloud_deploy_install.return_value = [
            base.SUBCLOUD_RESOURCE]
        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              cmd.InstallPhasedSubcloudDeploy,
                              app_args=[base.NAME,
                                        '--install-values', file_path]
                              )
        self.assertTrue('install-values does not exist'
                        in str(e))

    def test_configure_subcloud(self):
        self.client.subcloud_deploy_config.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)
            actual_call = self.call(
                cmd.ConfigPhasedSubcloudDeploy,
                app_args=[base.NAME, '--deploy-config', file_path])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_configure_file_does_not_exist(self):
        self.client.subcloud_deploy_config.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile() as f:
            file_path = os.path.abspath(f.name)

        e = self.assertRaises(DCManagerClientException,
                              self.call,
                              cmd.ConfigPhasedSubcloudDeploy,
                              app_args=[base.NAME,
                                        '--deploy-config', file_path])
        self.assertTrue('deploy-config file does not exist' in str(e))

    def test_complete_subcloud_deployment(self):
        self.client.subcloud_deploy_complete.return_value = [
            base.SUBCLOUD_RESOURCE]
        actual_call = self.call(
            cmd.CompletePhasedSubcloudDeploy,
            app_args=[base.NAME])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_abort_subcloud(self):
        self.client.subcloud_deploy_abort.return_value = [
            base.SUBCLOUD_RESOURCE]
        actual_call = self.call(
            cmd.AbortPhasedSubcloudDeploy,
            app_args=[base.NAME])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_subcloud_deploy_resume_all_parameters(self):
        self.client.subcloud_deploy_resume.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as bootstrap_file,\
            tempfile.NamedTemporaryFile(mode='w') as config_file,\
            tempfile.NamedTemporaryFile(mode='w') as install_file:

            bootstrap_file_path = os.path.abspath(bootstrap_file.name)
            config_file_path = os.path.abspath(config_file.name)
            install_file_path = os.path.abspath(install_file.name)

            actual_call = self.call(
                cmd.PhasedSubcloudDeployResume, app_args=[
                    base.NAME,
                    '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                    '--bootstrap-values', bootstrap_file_path,
                    '--install-values', install_file_path,
                    '--deploy-config', config_file_path,
                    '--release', base.SOFTWARE_VERSION,
                ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_subcloud_deploy_resume_missing_files(self):
        self.client.subcloud_deploy_resume.return_value = [
            base.SUBCLOUD_RESOURCE]

        with tempfile.NamedTemporaryFile(mode='w') as bootstrap_file,\
            tempfile.NamedTemporaryFile(mode='w') as config_file,\
            tempfile.NamedTemporaryFile(mode='w') as install_file:

            bootstrap_file_path = os.path.abspath(bootstrap_file.name)
            config_file_path = os.path.abspath(config_file.name)
            install_file_path = os.path.abspath(install_file.name)

        # Missing bootstrap values
        app_args_bootstrap = [base.NAME,
                              '--bootstrap-address', base.BOOTSTRAP_ADDRESS,
                              '--bootstrap-values', bootstrap_file_path]
        error_msg_bootstrap = 'bootstrap-values does not exist'
        call_bootstrap = self.assertRaises(DCManagerClientException,
                                           self.call,
                                           cmd.PhasedSubcloudDeployResume,
                                           app_args=app_args_bootstrap)
        self.assertTrue(error_msg_bootstrap in str(call_bootstrap))

        # Missing install values
        app_args_install = [base.NAME, '--install-values', install_file_path]
        error_msg_install = 'install-values does not exist'
        call_install = self.assertRaises(DCManagerClientException,
                                         self.call,
                                         cmd.PhasedSubcloudDeployResume,
                                         app_args=app_args_install)
        self.assertTrue(error_msg_install in str(call_install))

        # Missing deploy config values
        app_args_config = [base.NAME, '--deploy-config', config_file_path]
        error_msg_config = 'deploy-config does not exist'
        call_config = self.assertRaises(DCManagerClientException,
                                        self.call,
                                        cmd.PhasedSubcloudDeployResume,
                                        app_args=app_args_config)
        self.assertTrue(error_msg_config in str(call_config))

    def test_subcloud_deploy_resume_no_parameters(self):
        self.client.subcloud_deploy_resume.return_value = [
            base.SUBCLOUD_RESOURCE]

        actual_call = self.call(
            cmd.PhasedSubcloudDeployResume,
            app_args=[base.NAME])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])

    def test_subcloud_deploy_resume_no_files_only_release(self):
        self.client.subcloud_deploy_resume.return_value = [
            base.SUBCLOUD_RESOURCE]

        actual_call = self.call(
            cmd.PhasedSubcloudDeployResume, app_args=[
                base.NAME,
                '--release', base.SOFTWARE_VERSION,
            ])
        self.assertEqual(
            base.SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA,
            actual_call[1])
