#
# Copyright (c) 2022-2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64
import os

import mock

from dcmanagerclient.commands.v1 import (
    subcloud_backup_manager as subcloud_backup_cmd,
)
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base

OVERRIDE_VALUES = """---
                  platform_backup_filename_prefix: test
                  openstack_app_name: test
                  backup_dir: test
                  """


class TestCLISubcloudBackUpManagerV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.client_manager.subcloud_backup_manager

    def test_backup_create_subcloud(self):
        self.client.backup_subcloud_create.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--local-only",
                "--registry-images",
                "--backup-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])

    def test_backup_create_group(self):
        self.client.backup_subcloud_create.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--group",
                "test",
                "--backup-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertEqual([base.SUBCLOUD_FIELD_RESULT_LIST], actual_call[1])

    def test_backup_create_group_subcloud(self):
        self.client.backup_subcloud_create.return_value = []

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--group",
                "test",
                "--local-only",
                "--backup-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertTrue(
            (
                "The command only applies to a single subcloud or a subcloud group, "
                "not both."
            )
            in str(e)
        )

    def test_backup_create_no_group_no_subcloud(self):
        self.client.backup_subcloud_create.return_value = []

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--local-only",
                "--backup-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            ("Please provide the subcloud or subcloud group name or id.") in str(e)
        )

    def test_backup_create_backup_value_not_a_file(self):
        self.client.backup_subcloud_create.return_value = []

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--local-only",
                "--backup-values",
                "notADirectory",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue("Backup-values file does not exist" in str(e))

    @mock.patch("getpass.getpass", return_value="testpassword")
    def test_backup_create_prompt_ask_for_password(self, _mock_getpass):
        self.client.backup_subcloud_create.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--group",
                "test",
                "--local-only",
                "--backup-values",
                backup_path,
            ],
        )
        self.assertEqual([base.SUBCLOUD_FIELD_RESULT_LIST], actual_call[1])

    def test_backup_create_local_only_registry_images(self):
        self.client.subcloud_backup_manager.backup_subcloud_create.return_value = []

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.CreateSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--registry-images",
                "--backup-values",
                "notADirectory",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            ("Option --registry-images can not be used without --local-only option.")
            in str(e)
        )

    def test_backup_delete_no_group_no_subcloud(self):
        self.client.backup_subcloud_delete.return_value = []

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.DeleteSubcloudBackup,
            app_args=[
                "release",
                "--local-only",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            ("Please provide the subcloud or subcloud group name or id.") in str(e)
        )

    def test_backup_delete_group_subcloud(self):
        self.client.backup_subcloud_delete.return_value = []

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.DeleteSubcloudBackup,
            app_args=[
                "release",
                "--subcloud",
                "subcloud1",
                "--group",
                "group1",
                "--local-only",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            (
                "This command only applies to a single subcloud or a subcloud group, "
                "not both."
            )
            in str(e)
        )

    def test_backup_delete_group(self):
        group_name = "test_group_1"
        release_version = "release_version_2"
        password = "testpassword"
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        payload = {
            "release": release_version,
            "group": group_name,
            "local_only": "true",
            "sysadmin_password": encoded_password,
        }

        app_args = [
            release_version,
            "--group",
            group_name,
            "--local-only",
            "--sysadmin-password",
            password,
        ]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.backup_subcloud_delete.assert_called_once_with(
            data=payload, release_version=release_version, subcloud_ref=None
        )

    def test_backup_delete_subcloud(self):
        subcloud_name = "subcloud1"
        release_version = "release_version_2"
        password = "testpassword"
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        payload = {
            "release": release_version,
            "subcloud": subcloud_name,
            "local_only": "true",
            "sysadmin_password": encoded_password,
        }

        app_args = [
            release_version,
            "--subcloud",
            subcloud_name,
            "--local-only",
            "--sysadmin-password",
            password,
        ]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.backup_subcloud_delete.assert_called_once_with(
            data=payload, release_version=release_version, subcloud_ref=subcloud_name
        )

    def test_backup_delete_no_local_only(self):
        group_name = "test_group_1"
        release_version = "release_version_2"
        password = "testpassword"
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        payload = {
            "release": release_version,
            "group": group_name,
            "local_only": "false",
            "sysadmin_password": encoded_password,
        }

        app_args = [
            release_version,
            "--group",
            group_name,
            "--sysadmin-password",
            password,
        ]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.backup_subcloud_delete.assert_called_once_with(
            data=payload, release_version=release_version, subcloud_ref=None
        )

    @mock.patch("getpass.getpass", return_value="testpassword")
    def test_backup_delete_prompt_ask_for_password(self, _mock_getpass):
        group_name = "test_group_1"
        release_version = "release_version_2"
        password = "testpassword"
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        payload = {
            "release": release_version,
            "group": group_name,
            "local_only": "true",
            "sysadmin_password": encoded_password,
        }

        app_args = [release_version, "--group", group_name, "--local-only"]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.backup_subcloud_delete.assert_called_once_with(
            data=payload, release_version=release_version, subcloud_ref=None
        )

    def test_backup_delete_subcloud_no_release_version(self):
        subcloud_name = "subcloud1"
        password = "testpassword"

        app_args = [
            "--subcloud",
            subcloud_name,
            "--local-only",
            "--sysadmin-password",
            password,
        ]

        self.assertRaises(
            SystemExit,
            self.call,
            subcloud_backup_cmd.DeleteSubcloudBackup,
            app_args=app_args,
        )

    def _test_backup_delete_with_index(self, backup_index):
        subcloud_name = "subcloud1"
        release_version = "22.12"
        password = "testpassword"
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")

        payload = {
            "release": release_version,
            "subcloud": subcloud_name,
            "local_only": "false",
            "backup_index": backup_index,
            "sysadmin_password": encoded_password,
        }

        app_args = [
            release_version,
            "--subcloud",
            subcloud_name,
            "--backup-index",
            backup_index,
            "--sysadmin-password",
            password,
        ]

        self.call(subcloud_backup_cmd.DeleteSubcloudBackup, app_args=app_args)

        self.client.backup_subcloud_delete.assert_called_once_with(
            data=payload, release_version=release_version, subcloud_ref=subcloud_name
        )

    def test_backup_delete_with_backup_index(self):
        self._test_backup_delete_with_index("0")

    def test_backup_delete_with_backup_index_latest(self):
        self._test_backup_delete_with_index("latest")

    def test_backup_delete_with_backup_index_oldest(self):
        self._test_backup_delete_with_index("oldest")

    def test_backup_delete_local_only_with_backup_index_fails(self):
        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.DeleteSubcloudBackup,
            app_args=[
                "22.12",
                "--subcloud",
                "subcloud1",
                "--local-only",
                "--backup-index",
                "0",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            (
                "--backup-index parameter cannot be used with --local-only. "
                "Index-based deletion is only supported for centralized backups."
            )
            in str(e)
        )

    def _test_backup_delete_invalid_index(self, backup_index):
        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.DeleteSubcloudBackup,
            app_args=[
                "22.12",
                "--subcloud",
                "subcloud1",
                "--backup-index",
                backup_index,
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertTrue(
            "--backup-index must be a non-negative integer, 'latest', or 'oldest'."
            in str(e)
        )

    def test_backup_delete_with_invalid_backup_index_negative(self):
        self._test_backup_delete_invalid_index("-1")

    def test_backup_delete_with_invalid_backup_index_string(self):
        self._test_backup_delete_invalid_index("invalid")

    def test_backup_restore(self):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--local-only",
                "--registry-images",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])

    def test_backup_restore_no_restore_values(self):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        actual_call = self.call(
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--local-only",
                "--registry-images",
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])

    def test_backup_restore_with_group(self):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--group",
                "test",
                "--with-install",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertEqual([base.SUBCLOUD_FIELD_RESULT_LIST], actual_call[1])

    def test_backup_restore_group_and_subcloud(self):
        self.client.backup_subcloud_restore.return_value = []

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))

        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--group",
                "test",
                "--local-only",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )
        self.assertTrue(
            (
                "The command only applies to a single subcloud or a subcloud group, "
                "not both."
            )
            in str(e)
        )

    def test_backup_restore_no_group_and_no_subcloud(self):
        self.client.backup_subcloud_restore.return_value = []

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))

        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--local-only",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            ("Please provide the subcloud or subcloud group name or id.") in str(e)
        )

    def test_backup_restore_backup_value_not_a_file(self):
        self.client.backup_subcloud_restore.return_value = []

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--local-only",
                "--restore-values",
                "notADirectory",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue("restore_values file does not exist" in str(e))

    @mock.patch("getpass.getpass", return_value="testpassword")
    def test_backup_restore_prompt_ask_for_password(self, _mock_getpass):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))

        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--group",
                "test",
                "--local-only",
                "--restore-values",
                backup_path,
            ],
        )
        self.assertEqual([base.SUBCLOUD_FIELD_RESULT_LIST], actual_call[1])

    def test_backup_restore_local_only_registry_images(self):
        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--registry-images",
                "--restore-values",
                "notADirectory",
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            ("Option --registry-images cannot be used without --local-only option.")
            in str(e)
        )

    def test_backup_restore_with_install_no_release(self):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--with-install",
                "--local-only",
                "--registry-images",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])

    def test_backup_restore_with_install_with_release(self):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        actual_call = self.call(
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--with-install",
                "--release",
                base.SOFTWARE_VERSION,
                "--local-only",
                "--registry-images",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertEqual(base.SUBCLOUD_FIELD_RESULT_LIST, actual_call[1])

    def test_backup_restore_no_install_with_release(self):
        self.client.backup_subcloud_restore.return_value = [base.SUBCLOUD_RESOURCE]

        backup_path = os.path.normpath(os.path.join(os.getcwd(), "test.yaml"))
        with open(backup_path, mode="w", encoding="UTF-8") as f:
            f.write(OVERRIDE_VALUES)

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.RestoreSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--release",
                base.SOFTWARE_VERSION,
                "--local-only",
                "--registry-images",
                "--restore-values",
                backup_path,
                "--sysadmin-password",
                "testpassword",
            ],
        )

        self.assertTrue(
            (
                "Option --release cannot be used without --with-install "
                "or --factory option."
            )
            in str(e)
        )


class TestCLISubcloudBackList(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.client_manager.subcloud_backup_manager

        self.backup = {
            "subcloud": "subcloud1",
            "backup_index": 0,
            "backup_id": "backup-123",
            "release": "22.12",
            "created_at": "2025-01-15T10:30:45.123456",
            "size_bytes": 10485760,
            "storage": "dc-vault",
        }

    def test_backup_list_format_with_backup(self):
        columns, data = subcloud_backup_cmd.backup_list_format(self.backup)
        self.assertEqual(
            columns,
            ("Subcloud", "Index", "Backup ID", "Release", "Created", "Size", "Storage"),
        )
        self.assertEqual(
            data,
            (
                "subcloud1",
                "0 (latest)",
                "backup-123",
                "22.12",
                "2025-01-15 10:30:45",
                "10.0 MB",
                "dc-vault",
            ),
        )

    def test_backup_list_format_with_non_latest_backup(self):
        self.backup["backup_index"] = 2
        _, data = subcloud_backup_cmd.backup_list_format(self.backup)
        self.assertEqual(data[1], "2")

    def test_backup_list_format_without_backup(self):
        columns, data = subcloud_backup_cmd.backup_list_format(None)
        self.assertEqual(
            columns,
            ("Subcloud", "Index", "Backup ID", "Release", "Created", "Size", "Storage"),
        )
        self.assertEqual(data, (("<none>",) * 7,))

    def test_backup_list_no_filters(self):
        self.client.subcloud_backup_list.return_value = [self.backup]
        self.call(
            subcloud_backup_cmd.ListSubcloudBackup,
            app_args=[],
        )
        self.client.subcloud_backup_list.assert_called_once_with(
            subcloud=None, group=None, release=None, storage=None
        )

    def test_backup_list_with_filters(self):
        self.client.subcloud_backup_list.return_value = [self.backup]
        self.call(
            subcloud_backup_cmd.ListSubcloudBackup,
            app_args=[
                "--subcloud",
                "subcloud1",
                "--release",
                "22.12",
                "--storage",
                "seaweedfs",
            ],
        )
        self.client.subcloud_backup_list.assert_called_once_with(
            subcloud="subcloud1", group=None, release="22.12", storage="seaweedfs"
        )

    def test_backup_list_with_group_filter(self):
        self.client.subcloud_backup_list.return_value = [self.backup]
        self.call(
            subcloud_backup_cmd.ListSubcloudBackup,
            app_args=[
                "--group",
                "group1",
            ],
        )
        self.client.subcloud_backup_list.assert_called_once_with(
            subcloud=None, group="group1", release=None, storage=None
        )

    def test_backup_list_with_group_and_subcloud_filter_fails(self):
        self.client.subcloud_backup_list.return_value = [self.backup]
        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            subcloud_backup_cmd.ListSubcloudBackup,
            app_args=[
                "--group",
                "group1",
                "--subcloud",
                "subcloud1",
            ],
        )
        self.assertTrue(
            ("The '--subcloud' and '--group' parameters are mutually exclusive")
            in str(e)
        )
