# Copyright (c) 2020-2022 Wind River Systems, Inc.
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

import os
import tempfile

from dcmanagerclient.api.v1 import subcloud_deploy_manager as sdm
from dcmanagerclient.commands.v1 \
    import subcloud_deploy_manager as subcloud_deploy_cmd
from dcmanagerclient.tests import base


DEPLOY_PLAYBOOK = 'deployment-manager-playbook.yaml'
DEPLOY_OVERRIDES = 'deployment-manager-overrides-subcloud.yaml'
DEPLOY_CHART = 'deployment-manager.tgz'
DEPLOY_PRESTAGE_IMAGES = 'prebuilt-images.lst'

SUBCLOUD_DEPLOY_DICT = {
    'DEPLOY_PLAYBOOK': DEPLOY_PLAYBOOK,
    'DEPLOY_OVERRIDES': DEPLOY_OVERRIDES,
    'DEPLOY_CHART': DEPLOY_CHART,
    'DEPLOY_PRESTAGE_IMAGES': DEPLOY_PRESTAGE_IMAGES
}

SUBCLOUD_DEPLOY_ALL = sdm.SubcloudDeploy(
    deploy_playbook=SUBCLOUD_DEPLOY_DICT['DEPLOY_PLAYBOOK'],
    deploy_overrides=SUBCLOUD_DEPLOY_DICT['DEPLOY_OVERRIDES'],
    deploy_chart=SUBCLOUD_DEPLOY_DICT['DEPLOY_CHART'],
    prestage_images=SUBCLOUD_DEPLOY_DICT['DEPLOY_PRESTAGE_IMAGES']
)

SUBCLOUD_DEPLOY_PRESTAGE = sdm.SubcloudDeploy(
    prestage_images=SUBCLOUD_DEPLOY_DICT['DEPLOY_PRESTAGE_IMAGES']
)

SUBCLOUD_DEPLOY_NO_PRESTAGE = sdm.SubcloudDeploy(
    deploy_playbook=SUBCLOUD_DEPLOY_DICT['DEPLOY_PLAYBOOK'],
    deploy_overrides=SUBCLOUD_DEPLOY_DICT['DEPLOY_OVERRIDES'],
    deploy_chart=SUBCLOUD_DEPLOY_DICT['DEPLOY_CHART']
)

SUBCLOUD_DEPLOY_NO_PLAYBOOK = sdm.SubcloudDeploy(
    deploy_overrides=SUBCLOUD_DEPLOY_DICT['DEPLOY_OVERRIDES'],
    deploy_chart=SUBCLOUD_DEPLOY_DICT['DEPLOY_CHART'],
    prestage_images=SUBCLOUD_DEPLOY_DICT['DEPLOY_PRESTAGE_IMAGES']
)

SUBCLOUD_DEPLOY_NO_PLAYBOOK_OVERRIDES = sdm.SubcloudDeploy(
    deploy_chart=SUBCLOUD_DEPLOY_DICT['DEPLOY_CHART'],
    prestage_images=SUBCLOUD_DEPLOY_DICT['DEPLOY_PRESTAGE_IMAGES']
)

SUBCLOUD_DEPLOY_NO_OVERRIDES_CHART = sdm.SubcloudDeploy(
    deploy_playbook=SUBCLOUD_DEPLOY_DICT['DEPLOY_PLAYBOOK'],
    prestage_images=SUBCLOUD_DEPLOY_DICT['DEPLOY_PRESTAGE_IMAGES']
)


class TestCLISubcloudDeployManagerV1(base.BaseCommandTest):

    def setUp(self):
        super(TestCLISubcloudDeployManagerV1, self).setUp()
        # The client is the subcloud_deploy_manager
        self.client = self.app.client_manager.subcloud_deploy_manager

    def test_subcloud_deploy_show(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_show.\
            return_value = [SUBCLOUD_DEPLOY_ALL]
        actual_call = self.call(subcloud_deploy_cmd.SubcloudDeployShow)

        self.assertEqual((DEPLOY_PLAYBOOK,
                          DEPLOY_OVERRIDES,
                          DEPLOY_CHART,
                          DEPLOY_PRESTAGE_IMAGES),
                         actual_call[1])

    def test_subcloud_deploy_upload_all(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_ALL]

        with tempfile.NamedTemporaryFile() as f1,\
                tempfile.NamedTemporaryFile() as f2,\
                tempfile.NamedTemporaryFile() as f3,\
                tempfile.NamedTemporaryFile() as f4:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            file_path_4 = os.path.abspath(f4.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--deploy-playbook', file_path_1,
                    '--deploy-overrides', file_path_2,
                    '--deploy-chart', file_path_3,
                    '--prestage-images', file_path_4])

        self.assertEqual((DEPLOY_PLAYBOOK,
                          DEPLOY_OVERRIDES,
                          DEPLOY_CHART,
                          DEPLOY_PRESTAGE_IMAGES),
                         actual_call[1])

    def test_subcloud_deploy_upload_no_prestage(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_NO_PRESTAGE]

        with tempfile.NamedTemporaryFile() as f1,\
                tempfile.NamedTemporaryFile() as f2,\
                tempfile.NamedTemporaryFile() as f3:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--deploy-playbook', file_path_1,
                    '--deploy-overrides', file_path_2,
                    '--deploy-chart', file_path_3])

        self.assertEqual((DEPLOY_PLAYBOOK,
                          DEPLOY_OVERRIDES,
                          DEPLOY_CHART,
                          None),
                         actual_call[1])

    def test_subcloud_deploy_upload_prestage(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_PRESTAGE]

        with tempfile.NamedTemporaryFile() as f1:
            file_path_1 = os.path.abspath(f1.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--prestage-images', file_path_1])
        self.assertEqual((None,
                          None,
                          None,
                          DEPLOY_PRESTAGE_IMAGES),
                         actual_call[1])

    def test_subcloud_deploy_upload_no_playbook(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_NO_PLAYBOOK]

        with tempfile.NamedTemporaryFile() as f1,\
                tempfile.NamedTemporaryFile() as f2,\
                tempfile.NamedTemporaryFile() as f3:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--deploy-overrides', file_path_1,
                    '--deploy-chart', file_path_2,
                    '--prestage-images', file_path_3])
            print(actual_call[1])
        self.assertEqual((None,
                          DEPLOY_OVERRIDES,
                          DEPLOY_CHART,
                          DEPLOY_PRESTAGE_IMAGES),
                         actual_call[1])

    def test_subcloud_deploy_upload_no_playbook_overrides(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_NO_PLAYBOOK_OVERRIDES]

        with tempfile.NamedTemporaryFile() as f1,\
                tempfile.NamedTemporaryFile() as f2:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--deploy-chart', file_path_1,
                    '--prestage-images', file_path_2])
            print(actual_call[1])
        self.assertEqual((None,
                          None,
                          DEPLOY_CHART,
                          DEPLOY_PRESTAGE_IMAGES),
                         actual_call[1])

    def test_subcloud_deploy_upload_no_overrides_chart(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_NO_OVERRIDES_CHART]

        with tempfile.NamedTemporaryFile() as f1,\
                tempfile.NamedTemporaryFile() as f2:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--deploy-playbook', file_path_1,
                    '--prestage-images', file_path_2])
            print(actual_call[1])
        self.assertEqual((DEPLOY_PLAYBOOK,
                          None,
                          None,
                          DEPLOY_PRESTAGE_IMAGES),
                         actual_call[1])

    def test_subcloud_deploy_upload_invalid_path(self):
        self.client.subcloud_deploy_manager.subcloud_deploy_upload.\
            return_value = [SUBCLOUD_DEPLOY_NO_PRESTAGE]
        file_path_1 = 'not_a_valid_path'
        with tempfile.NamedTemporaryFile() as f2,\
                tempfile.NamedTemporaryFile() as f3:
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            actual_call = self.call(
                subcloud_deploy_cmd.SubcloudDeployUpload,
                app_args=[
                    '--deploy-playbook', file_path_1,
                    '--deploy-overrides', file_path_2,
                    '--deploy-chart', file_path_3])

        self.assertEqual((None,
                          None,
                          None,
                          None),
                         actual_call[1])
