#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import (
    subcloud_backup_config_manager as sbcm,
)
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base


class TestCLISubcloudBackupConfigManagerV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.client_manager.subcloud_backup_config_manager

    def _create_mock_config(
        self, storage_location="dc-vault", retention_count=2, updated_at=None
    ):
        """Helper to create mock config dictionaries"""
        config = {
            "storage_location": storage_location,
            "retention_count": retention_count,
        }
        if updated_at:
            config["updated_at"] = updated_at
        return config

    def _assert_output_matches(self, actual_call, storage, retention, updated_at):
        """Helper to verify output format"""
        expected_columns = ("Storage Location", "Retention Count", "Updated At")
        expected_data = (storage, str(retention), updated_at)
        self.assertEqual(expected_columns, actual_call[0])
        self.assertEqual(expected_data, actual_call[1])

    def test_backup_config_show(self):
        """Test showing backup configuration"""
        mock_config = self._create_mock_config(updated_at="2026-01-08T10:30:45.123456")
        self.client.subcloud_backup_config_show.return_value = mock_config

        actual_call = self.call(sbcm.ShowSubcloudBackupConfig)

        self.client.subcloud_backup_config_show.assert_called_once()
        self._assert_output_matches(actual_call, "dc-vault", 2, "2026-01-08 10:30:45")

    def test_backup_config_show_with_missing_updated_at(self):
        """Test showing backup configuration with missing updated_at field"""
        mock_config = self._create_mock_config()
        self.client.subcloud_backup_config_show.return_value = mock_config

        actual_call = self.call(sbcm.ShowSubcloudBackupConfig)

        self._assert_output_matches(actual_call, "dc-vault", 2, "")

    def test_backup_config_update_storage_location(self):
        """Test updating storage location"""
        mock_config = self._create_mock_config(
            storage_location="seaweedfs", updated_at="2026-01-08T11:00:00.000000"
        )
        self.client.subcloud_backup_config_update.return_value = mock_config

        actual_call = self.call(
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--storage-location", "seaweedfs"],
        )

        self.client.subcloud_backup_config_update.assert_called_once_with(
            storage_location="seaweedfs"
        )
        self._assert_output_matches(actual_call, "seaweedfs", 2, "2026-01-08 11:00:00")

    def test_backup_config_update_retention_count(self):
        """Test updating retention count"""
        mock_config = self._create_mock_config(
            retention_count=5, updated_at="2026-01-08T12:00:00.000000"
        )
        self.client.subcloud_backup_config_update.return_value = mock_config

        actual_call = self.call(
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--retention-count", "5"],
        )

        self.client.subcloud_backup_config_update.assert_called_once_with(
            retention_count=5
        )
        self._assert_output_matches(actual_call, "dc-vault", 5, "2026-01-08 12:00:00")

    def test_backup_config_update_both_parameters(self):
        """Test updating both storage location and retention count"""
        mock_config = self._create_mock_config(
            storage_location="seaweedfs",
            retention_count=7,
            updated_at="2026-01-08T13:00:00.000000",
        )
        self.client.subcloud_backup_config_update.return_value = mock_config

        actual_call = self.call(
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--storage-location", "seaweedfs", "--retention-count", "7"],
        )

        self.client.subcloud_backup_config_update.assert_called_once_with(
            storage_location="seaweedfs", retention_count=7
        )
        self._assert_output_matches(actual_call, "seaweedfs", 7, "2026-01-08 13:00:00")

    def test_backup_config_update_retention_count_boundary_values(self):
        """Test retention count with boundary values (min=1, max=10)"""
        mock_config = self._create_mock_config(
            retention_count=1, updated_at="2026-01-08T14:00:00.000000"
        )
        self.client.subcloud_backup_config_update.return_value = mock_config

        # minimum value
        actual_call = self.call(
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--retention-count", "1"],
        )
        self._assert_output_matches(actual_call, "dc-vault", 1, "2026-01-08 14:00:00")

        # maximum value
        mock_config["retention_count"] = 10
        actual_call = self.call(
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--retention-count", "10"],
        )
        self._assert_output_matches(actual_call, "dc-vault", 10, "2026-01-08 14:00:00")

    def test_backup_config_update_no_parameters(self):
        """Test update with no parameters should fail"""
        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            sbcm.UpdateSubcloudBackupConfig,
            app_args=[],
        )

        self.assertIn(
            "At least one parameter (--storage-location or --retention-count) "
            "must be provided",
            str(e),
        )
        self.client.subcloud_backup_config_update.assert_not_called()

    def _test_invalid_retention_count(self, value):
        """Helper to test invalid retention count values"""
        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--retention-count", value],
        )
        self.assertIn("retention_count must be between 1 and 10", str(e))

    def test_backup_config_update_retention_count_zero(self):
        """Test updating retention count to 0 should fail"""
        self._test_invalid_retention_count("0")
        self.client.subcloud_backup_config_update.assert_not_called()

    def test_backup_config_update_retention_count_negative(self):
        """Test updating retention count to negative value should fail"""
        self._test_invalid_retention_count("-1")
        self.client.subcloud_backup_config_update.assert_not_called()

    def test_backup_config_update_retention_count_above_maximum(self):
        """Test updating retention count to value > 10 should fail"""
        self._test_invalid_retention_count("11")
        self.client.subcloud_backup_config_update.assert_not_called()

    def test_backup_config_update_invalid_storage_location(self):
        """Test updating storage location to invalid value should fail"""
        self.assertRaises(
            SystemExit,
            self.call,
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--storage-location", "invalid-storage"],
        )
        self.client.subcloud_backup_config_update.assert_not_called()

    def test_backup_config_update_api_error(self):
        """Test handling of API errors during update"""
        self.client.subcloud_backup_config_update.side_effect = Exception(
            "API Error: Connection failed"
        )

        e = self.assertRaises(
            DCManagerClientException,
            self.call,
            sbcm.UpdateSubcloudBackupConfig,
            app_args=["--storage-location", "seaweedfs"],
        )

        self.assertIn("Unable to update backup configuration", str(e))
        self.assertIn("API Error: Connection failed", str(e))
        self.client.subcloud_backup_config_update.assert_called_once()

    def test_backup_config_format_with_valid_config(self):
        """Test config_format function with valid config"""
        test_config = self._create_mock_config(
            storage_location="seaweedfs",
            retention_count=3,
            updated_at="2026-01-08T16:45:30.123456",
        )

        columns, data = sbcm.config_format(test_config)

        expected_columns = ("Storage Location", "Retention Count", "Updated At")
        expected_data = ("seaweedfs", "3", "2026-01-08 16:45:30")

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, data)
