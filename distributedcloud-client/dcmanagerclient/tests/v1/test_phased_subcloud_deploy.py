#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import mock
import os
import tempfile

from dcmanagerclient.commands.v1 import phased_subcloud_deploy_manager as cmd
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
        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])

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
        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])
