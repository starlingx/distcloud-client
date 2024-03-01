# Copyright (c) 2020-2024 Wind River Systems, Inc.
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

import mock

from dcmanagerclient.api.v1 import subcloud_deploy_manager as sdm
from dcmanagerclient.commands.v1 import subcloud_deploy_manager
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base

DEPLOY_PLAYBOOK = "deployment-manager-playbook.yaml"
DEPLOY_OVERRIDES = "deployment-manager-overrides-subcloud.yaml"
DEPLOY_CHART = "deployment-manager.tgz"
DEPLOY_PRESTAGE_IMAGES = "prebuilt-images.lst"

SUBCLOUD_DEPLOY_DICT = {
    "DEPLOY_PLAYBOOK": DEPLOY_PLAYBOOK,
    "DEPLOY_OVERRIDES": DEPLOY_OVERRIDES,
    "DEPLOY_CHART": DEPLOY_CHART,
    "DEPLOY_PRESTAGE_IMAGES": DEPLOY_PRESTAGE_IMAGES,
    "SOFTWARE_VERSION": base.SOFTWARE_VERSION,
}

SUBCLOUD_DEPLOY_ALL = sdm.SubcloudDeploy(
    deploy_playbook=SUBCLOUD_DEPLOY_DICT["DEPLOY_PLAYBOOK"],
    deploy_overrides=SUBCLOUD_DEPLOY_DICT["DEPLOY_OVERRIDES"],
    deploy_chart=SUBCLOUD_DEPLOY_DICT["DEPLOY_CHART"],
    prestage_images=SUBCLOUD_DEPLOY_DICT["DEPLOY_PRESTAGE_IMAGES"],
    software_version=SUBCLOUD_DEPLOY_DICT["SOFTWARE_VERSION"],
)

SUBCLOUD_DEPLOY_PRESTAGE = sdm.SubcloudDeploy(
    prestage_images=SUBCLOUD_DEPLOY_DICT["DEPLOY_PRESTAGE_IMAGES"],
    software_version=SUBCLOUD_DEPLOY_DICT["SOFTWARE_VERSION"],
)

SUBCLOUD_DEPLOY_NO_PRESTAGE = sdm.SubcloudDeploy(
    deploy_playbook=SUBCLOUD_DEPLOY_DICT["DEPLOY_PLAYBOOK"],
    deploy_overrides=SUBCLOUD_DEPLOY_DICT["DEPLOY_OVERRIDES"],
    deploy_chart=SUBCLOUD_DEPLOY_DICT["DEPLOY_CHART"],
    software_version=SUBCLOUD_DEPLOY_DICT["SOFTWARE_VERSION"],
)

SUBCLOUD_DEPLOY_NO_PLAYBOOK = sdm.SubcloudDeploy(
    deploy_overrides=SUBCLOUD_DEPLOY_DICT["DEPLOY_OVERRIDES"],
    deploy_chart=SUBCLOUD_DEPLOY_DICT["DEPLOY_CHART"],
    prestage_images=SUBCLOUD_DEPLOY_DICT["DEPLOY_PRESTAGE_IMAGES"],
    software_version=SUBCLOUD_DEPLOY_DICT["SOFTWARE_VERSION"],
)

SUBCLOUD_DEPLOY_NO_PLAYBOOK_OVERRIDES = sdm.SubcloudDeploy(
    deploy_chart=SUBCLOUD_DEPLOY_DICT["DEPLOY_CHART"],
    prestage_images=SUBCLOUD_DEPLOY_DICT["DEPLOY_PRESTAGE_IMAGES"],
    software_version=SUBCLOUD_DEPLOY_DICT["SOFTWARE_VERSION"],
)

SUBCLOUD_DEPLOY_NO_OVERRIDES_CHART = sdm.SubcloudDeploy(
    deploy_playbook=SUBCLOUD_DEPLOY_DICT["DEPLOY_PLAYBOOK"],
    prestage_images=SUBCLOUD_DEPLOY_DICT["DEPLOY_PRESTAGE_IMAGES"],
    software_version=SUBCLOUD_DEPLOY_DICT["SOFTWARE_VERSION"],
)


class TestCLISubcloudDeployManagerV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        # The client is the subcloud_deploy_manager
        self.client = self.app.client_manager.subcloud_deploy_manager

    def test_subcloud_deploy_show(self):
        self.client.subcloud_deploy_show.return_value = [SUBCLOUD_DEPLOY_ALL]

        # Without "--release" parameter
        actual_call1 = self.call(subcloud_deploy_manager.SubcloudDeployShow)

        self.assertEqual(
            (
                DEPLOY_PLAYBOOK,
                DEPLOY_OVERRIDES,
                DEPLOY_CHART,
                DEPLOY_PRESTAGE_IMAGES,
                base.SOFTWARE_VERSION,
            ),
            actual_call1[1],
        )

        # With "--release" parameter
        actual_call2 = self.call(
            subcloud_deploy_manager.SubcloudDeployShow,
            app_args=["--release", base.SOFTWARE_VERSION],
        )

        self.assertEqual(
            (
                DEPLOY_PLAYBOOK,
                DEPLOY_OVERRIDES,
                DEPLOY_CHART,
                DEPLOY_PRESTAGE_IMAGES,
                base.SOFTWARE_VERSION,
            ),
            actual_call2[1],
        )

    def test_subcloud_deploy_upload_all(self):
        self.client.subcloud_deploy_upload.return_value = [SUBCLOUD_DEPLOY_ALL]

        f1 = tempfile.NamedTemporaryFile()
        f2 = tempfile.NamedTemporaryFile()
        f3 = tempfile.NamedTemporaryFile()
        f4 = tempfile.NamedTemporaryFile()

        with f1, f2, f3, f4:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            file_path_4 = os.path.abspath(f4.name)
            actual_call = self.call(
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=[
                    "--deploy-playbook",
                    file_path_1,
                    "--deploy-overrides",
                    file_path_2,
                    "--deploy-chart",
                    file_path_3,
                    "--prestage-images",
                    file_path_4,
                ],
            )

        self.assertEqual(
            (
                DEPLOY_PLAYBOOK,
                DEPLOY_OVERRIDES,
                DEPLOY_CHART,
                DEPLOY_PRESTAGE_IMAGES,
                base.SOFTWARE_VERSION,
            ),
            actual_call[1],
        )

    def test_subcloud_deploy_upload_no_prestage(self):
        self.client.subcloud_deploy_upload.return_value = [SUBCLOUD_DEPLOY_NO_PRESTAGE]

        f1 = tempfile.NamedTemporaryFile()
        f2 = tempfile.NamedTemporaryFile()
        f3 = tempfile.NamedTemporaryFile()

        with f1, f2, f3:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            actual_call = self.call(
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=[
                    "--deploy-playbook",
                    file_path_1,
                    "--deploy-overrides",
                    file_path_2,
                    "--deploy-chart",
                    file_path_3,
                ],
            )

        self.assertEqual(
            (
                DEPLOY_PLAYBOOK,
                DEPLOY_OVERRIDES,
                DEPLOY_CHART,
                None,
                base.SOFTWARE_VERSION,
            ),
            actual_call[1],
        )

    def test_subcloud_deploy_upload_prestage(self):
        self.client.subcloud_deploy_upload.return_value = [SUBCLOUD_DEPLOY_PRESTAGE]

        with tempfile.NamedTemporaryFile() as f1:
            file_path_1 = os.path.abspath(f1.name)
            actual_call = self.call(
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=["--prestage-images", file_path_1],
            )
        self.assertEqual(
            (None, None, None, DEPLOY_PRESTAGE_IMAGES, base.SOFTWARE_VERSION),
            actual_call[1],
        )

    def test_subcloud_deploy_upload_no_playbook(self):
        self.client.subcloud_deploy_upload.return_value = [SUBCLOUD_DEPLOY_NO_PLAYBOOK]

        f1 = tempfile.NamedTemporaryFile()
        f2 = tempfile.NamedTemporaryFile()
        f3 = tempfile.NamedTemporaryFile()

        with f1, f2, f3:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)
            actual_call = self.call(
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=[
                    "--deploy-overrides",
                    file_path_1,
                    "--deploy-chart",
                    file_path_2,
                    "--prestage-images",
                    file_path_3,
                ],
            )
        self.assertEqual(
            (
                None,
                DEPLOY_OVERRIDES,
                DEPLOY_CHART,
                DEPLOY_PRESTAGE_IMAGES,
                base.SOFTWARE_VERSION,
            ),
            actual_call[1],
        )

    def test_subcloud_deploy_upload_no_playbook_overrides(self):
        self.client.subcloud_deploy_upload.return_value = [
            SUBCLOUD_DEPLOY_NO_PLAYBOOK_OVERRIDES
        ]

        f1 = tempfile.NamedTemporaryFile()
        f2 = tempfile.NamedTemporaryFile()

        with f1, f2:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            actual_call = self.call(
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=[
                    "--deploy-chart",
                    file_path_1,
                    "--prestage-images",
                    file_path_2,
                ],
            )
        self.assertEqual(
            (
                None,
                None,
                DEPLOY_CHART,
                DEPLOY_PRESTAGE_IMAGES,
                base.SOFTWARE_VERSION,
            ),
            actual_call[1],
        )

    def test_subcloud_deploy_upload_no_overrides_chart(self):
        self.client.subcloud_deploy_upload.return_value = [
            SUBCLOUD_DEPLOY_NO_OVERRIDES_CHART
        ]

        f1 = tempfile.NamedTemporaryFile()
        f2 = tempfile.NamedTemporaryFile()

        with f1, f2:
            file_path_1 = os.path.abspath(f1.name)
            file_path_2 = os.path.abspath(f2.name)
            actual_call = self.call(
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=[
                    "--deploy-playbook",
                    file_path_1,
                    "--prestage-images",
                    file_path_2,
                    "--release",
                    base.SOFTWARE_VERSION,
                ],
            )
        self.assertEqual(
            (
                DEPLOY_PLAYBOOK,
                None,
                None,
                DEPLOY_PRESTAGE_IMAGES,
                base.SOFTWARE_VERSION,
            ),
            actual_call[1],
        )

    @mock.patch("builtins.print")
    def test_subcloud_deploy_upload_invalid_path(self, mock_print):
        self.client.subcloud_deploy_upload.return_value = [SUBCLOUD_DEPLOY_NO_PRESTAGE]
        mock_print.return_value = mock.ANY
        file_path_1 = "not_a_valid_path"

        f2 = tempfile.NamedTemporaryFile()
        f3 = tempfile.NamedTemporaryFile()

        with f2, f3:
            file_path_2 = os.path.abspath(f2.name)
            file_path_3 = os.path.abspath(f3.name)

            e = self.assertRaises(
                DCManagerClientException,
                self.call,
                subcloud_deploy_manager.SubcloudDeployUpload,
                app_args=[
                    "--deploy-playbook",
                    file_path_1,
                    "--deploy-overrides",
                    file_path_2,
                    "--deploy-chart",
                    file_path_3,
                ],
            )

        self.assertTrue(
            "deploy_playbook file does not exist: not_a_valid_path" in str(e)
        )

    def test_subcloud_deploy_delete_with_release(self):
        release_version = base.SOFTWARE_VERSION
        data = {"prestage_images": "False", "deployment_files": "False"}
        app_args = ["--release", release_version]

        self.call(subcloud_deploy_manager.SubcloudDeployDelete, app_args=app_args)

        self.client.subcloud_deploy_delete.assert_called_once_with(
            release_version, data=data
        )

    def test_subcloud_deploy_delete_without_release(self):
        self.call(subcloud_deploy_manager.SubcloudDeployDelete)
        data = {"prestage_images": "False", "deployment_files": "False"}
        self.client.subcloud_deploy_delete.assert_called_once_with(None, data=data)
