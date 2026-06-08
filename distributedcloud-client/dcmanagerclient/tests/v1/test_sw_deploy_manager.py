#
# Copyright (c) 2024-2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import mock

from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.commands.v1 import sw_deploy_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin
from dcmanagerclient.tests.v1 import utils

RELEASE_ID = "stx-10.01.100"


class TestSwDeployStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()

        # Increase results_length due to extra_args fields.
        # This includes release_id, snapshot, rollback, delete_option,
        # with_prestage and kube_upgrade
        self.results_length += 6

        self.sw_update_manager = self.app.client_manager.sw_deploy_manager
        self.create_command = cli_cmd.CreateSwDeployStrategy
        self.show_command = cli_cmd.ShowSwDeployStrategy
        self.delete_command = cli_cmd.DeleteSwDeployStrategy
        self.apply_command = cli_cmd.ApplySwDeployStrategy
        self.abort_command = cli_cmd.AbortSwDeployStrategy

    def base_create_strategy_successful(
        self,
        release_id=None,
        snapshot=False,
        rollback=False,
        delete=False,
        cleanup=False,
        kube_upgrade=None,
    ):
        """Base method to create a software deploy strategy."""
        # Prepare mixin attributes
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        # Mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=expected_strategy_type,
            extra_args={
                "release_id": release_id,
                "snapshot": snapshot,
                "rollback": rollback,
                "delete": delete,
                "cleanup": cleanup,
                "kube_upgrade": kube_upgrade or "",
            },
        )

        # Mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = strategy

        # Invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        values = ["subcloud1"]
        if release_id:
            values.extend(["--release-id", release_id])
        if snapshot:
            values.append("--snapshot")
        if rollback:
            values.append("--rollback")
        if delete:
            values.append("--delete")
        if cleanup:
            values.append("--cleanup")
        if kube_upgrade:
            values.extend(["--kube-upgrade", kube_upgrade])
        fields, results = self.call(self.create_command, values)

        # Results is a tuple of expected length
        self.assertEqual(len(results), self.results_length)
        # Result tuple values are
        # - strategy type
        # - subcloud apply type
        # - max parallel subclouds
        # - stop on failure
        # - release_id
        # - snapshot
        # - rollback
        # - delete
        # - cleanup
        # - state
        # - created_at
        # - updated_at
        failure_index = fields.index("stop on failure")
        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(fields[failure_index + 1], "release_id")
        self.assertEqual(results[failure_index + 1], release_id)

        # Verify the manager was called with correct parameters
        manager_to_test.create_sw_update_strategy.assert_called_once()
        call_kwargs = manager_to_test.create_sw_update_strategy.call_args[1]
        self.assertEqual(call_kwargs.get("release_id"), release_id)
        self.assertEqual(call_kwargs.get("snapshot", False), snapshot)
        self.assertEqual(call_kwargs.get("rollback", False), rollback)
        self.assertEqual(call_kwargs.get("delete", False), delete)
        self.assertEqual(call_kwargs.get("cleanup", False), cleanup)
        if kube_upgrade:
            self.assertEqual(call_kwargs.get("kube_upgrade"), kube_upgrade)

    def base_create_strategy_failure(
        self,
        error_msg,
        release_id=None,
        snapshot=False,
        rollback=False,
        delete=False,
        sysadmin_password=None,
        kube_upgrade=None,
        cleanup=False,
        with_prestage=False,
    ):
        """Base method to test failure in creating a software deploy strategy."""

        # prepare mixin attributes
        manager_to_test = self.sw_update_manager

        # mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = None

        values = ["subcloud1"]
        if release_id:
            values.extend(["--release-id", release_id])
        if snapshot:
            values.append("--snapshot")
        if rollback:
            values.append("--rollback")
        if delete:
            values.append("--delete")
        if cleanup:
            values.append("--cleanup")
        if with_prestage:
            values.append("--with-prestage")
        if sysadmin_password:
            values.extend(["--sysadmin-password", sysadmin_password])
        if kube_upgrade:
            values.extend(["--kube-upgrade", kube_upgrade])

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        e = self.assertRaises(
            DCManagerClientException, self.call, self.create_command, values
        )
        self.assertTrue(error_msg in str(e))

    def test_create_strategy(self):
        """Test deploy strategy created with release_id"""
        self.base_create_strategy_successful(release_id=RELEASE_ID)

    def test_create_strategy_with_snapshot(self):
        """Test deploy strategy created with snapshot enabled"""
        self.base_create_strategy_successful(release_id=RELEASE_ID, snapshot=True)

    def test_create_strategy_delete(self):
        """Test deploy strategy created with delete enabled"""
        self.base_create_strategy_successful(release_id=RELEASE_ID, delete=True)

    def test_create_strategy_cleanup(self):
        """Test deploy strategy created with cleanup enabled"""
        self.base_create_strategy_successful(cleanup=True)

    def test_create_strategy_with_snapshot_and_delete(self):
        """Test deploy strategy created with snapshot and delete enabled"""
        self.base_create_strategy_successful(
            release_id=RELEASE_ID, snapshot=True, delete=True
        )

    def test_create_strategy_with_rollback(self):
        """Test deploy strategy created with rollback enabled"""
        self.base_create_strategy_successful(rollback=True)

    def test_create_strategy_without_release_id(self):
        """Test deploy strategy cannot created without release_id"""
        self.base_create_strategy_failure(self.create_command.RELEASE_ID_ERROR_MSG)

    def test_create_strategy_with_snapshot_and_rollback(self):
        """Test deploy strategy cannot created with snapshot and rollback"""
        self.base_create_strategy_failure(
            self.create_command.SNAPSHOT_ERROR_MSG,
            release_id=RELEASE_ID,
            snapshot=True,
            rollback=True,
        )

    def test_create_strategy_with_snapshot_and_cleanup(self):
        """Test deploy strategy cannot created with snapshot and cleanup"""
        self.base_create_strategy_failure(
            self.create_command.SNAPSHOT_ERROR_MSG,
            release_id=RELEASE_ID,
            snapshot=True,
            cleanup=True,
        )

    def test_create_strategy_with_rollback_and_release_id(self):
        """Test deploy strategy cannot created with rollback and release_id"""
        self.base_create_strategy_failure(
            self.create_command.ROLLBACK_ERROR_MSG,
            release_id=RELEASE_ID,
            rollback=True,
        )

    def test_create_strategy_sysadmin_password_without_prestage(self):
        """Test deploy strategy create with sysadmin_password and no prestage"""
        self.base_create_strategy_failure(
            self.create_command.WITH_PRESTAGE_ERROR_MSG,
            release_id=RELEASE_ID,
            sysadmin_password="XXXX",
        )

    def test_create_strategy_with_rollback_and_delete(self):
        """Test deploy strategy cannot created with rollback and delete"""
        self.base_create_strategy_failure(
            self.create_command.DELETE_ERROR_MSG, rollback=True, delete=True
        )

    def test_create_strategy_with_rollback_and_cleanup(self):
        """Test deploy strategy cannot created with rollback and cleanup"""
        self.base_create_strategy_failure(
            self.create_command.ROLLBACK_ERROR_MSG, rollback=True, cleanup=True
        )

    def test_create_strategy_with_delete_and_cleanup(self):
        """Test deploy strategy cannot created with delete and cleanup"""
        self.base_create_strategy_failure(
            self.create_command.DELETE_ERROR_MSG,
            release_id=RELEASE_ID,
            delete=True,
            cleanup=True,
        )

    def test_create_strategy_with_cleanup_and_release_id(self):
        """Test deploy strategy cannot created with cleanup and release_id"""
        self.base_create_strategy_failure(
            self.create_command.CLEANUP_ERROR_MSG,
            release_id=RELEASE_ID,
            cleanup=True,
        )

    def test_create_strategy_with_kube_upgrade(self):
        """Test deploy strategy created with kube_upgrade"""
        self.base_create_strategy_successful(
            release_id=RELEASE_ID, kube_upgrade="v1.28.4"
        )

    def test_create_strategy_with_kube_upgrade_and_delete(self):
        """Test deploy strategy created with kube_upgrade and delete"""
        self.base_create_strategy_successful(
            release_id=RELEASE_ID, kube_upgrade="v1.28.4", delete=True
        )

    def test_create_strategy_with_kube_upgrade_and_rollback(self):
        """Test deploy strategy cannot be created with kube_upgrade and rollback"""
        self.base_create_strategy_failure(
            self.create_command.ROLLBACK_ERROR_MSG,
            rollback=True,
            kube_upgrade="v1.28.4",
        )

    def test_create_strategy_with_kube_upgrade_and_cleanup(self):
        """Test deploy strategy cannot be created with kube_upgrade and cleanup"""
        self.base_create_strategy_failure(
            self.create_command.CLEANUP_ERROR_MSG,
            cleanup=True,
            kube_upgrade="v1.28.4",
        )

    def test_create_strategy_with_rollback_and_with_prestage(self):
        """Test deploy strategy cannot be created with rollback and with_prestage"""
        self.base_create_strategy_failure(
            self.create_command.ROLLBACK_ERROR_MSG,
            rollback=True,
            with_prestage=True,
            sysadmin_password="XXXX",
        )

    def test_create_strategy_with_cleanup_and_with_prestage(self):
        """Test deploy strategy cannot be created with cleanup and with_prestage"""
        self.base_create_strategy_failure(
            self.create_command.CLEANUP_ERROR_MSG,
            cleanup=True,
            with_prestage=True,
            sysadmin_password="XXXX",
        )

    def test_show_strategy_with_legacy_with_delete(self):
        """Test show maps legacy with_delete extra_arg to delete_option='delete'"""
        manager_to_test = self.sw_update_manager
        strategy = utils.make_strategy(
            strategy_type=manager_to_test.update_type,
            extra_args={
                "release_id": RELEASE_ID,
                "snapshot": False,
                "rollback": False,
                "with_delete": True,
                "with_prestage": False,
                "kube_upgrade": "",
            },
        )
        manager_to_test.update_sw_strategy_detail.return_value = strategy

        fields, results = self.call(self.show_command)
        delete_option_index = fields.index("delete_option")
        self.assertEqual(results[delete_option_index], "delete")

    def test_show_strategy_with_legacy_delete_only(self):
        """Test show maps legacy delete_only extra_arg to delete_option='cleanup'"""
        manager_to_test = self.sw_update_manager
        strategy = utils.make_strategy(
            strategy_type=manager_to_test.update_type,
            extra_args={
                "release_id": None,
                "snapshot": False,
                "rollback": False,
                "delete_only": True,
                "with_prestage": False,
                "kube_upgrade": "",
            },
        )
        manager_to_test.update_sw_strategy_detail.return_value = strategy

        fields, results = self.call(self.show_command)
        delete_option_index = fields.index("delete_option")
        self.assertEqual(results[delete_option_index], "cleanup")

    def test_show_strategy_with_kube_upgrade(self):
        """Test show displays kube_upgrade field correctly"""
        manager_to_test = self.sw_update_manager
        strategy = utils.make_strategy(
            strategy_type=manager_to_test.update_type,
            extra_args={
                "release_id": RELEASE_ID,
                "snapshot": False,
                "rollback": False,
                "delete": False,
                "with_prestage": False,
                "kube_upgrade": "v1.28.4",
            },
        )
        manager_to_test.update_sw_strategy_detail.return_value = strategy

        fields, results = self.call(self.show_command)
        kube_upgrade_index = fields.index("kube_upgrade")
        self.assertEqual(results[kube_upgrade_index], "v1.28.4")

    @mock.patch("dcmanagerclient.utils.print_deprecation_notice")
    def test_create_strategy_with_deprecated_with_delete(self, mock_deprecation):
        """Test --with-delete maps to --delete and prints deprecation notice"""
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        strategy = utils.make_strategy(
            strategy_type=expected_strategy_type,
            extra_args={
                "release_id": RELEASE_ID,
                "snapshot": False,
                "rollback": False,
                "delete": True,
                "cleanup": False,
                "kube_upgrade": "",
            },
        )
        manager_to_test.create_sw_update_strategy.return_value = strategy

        self.call(
            self.create_command,
            ["subcloud1", "--release-id", RELEASE_ID, "--with-delete"],
        )

        call_kwargs = manager_to_test.create_sw_update_strategy.call_args[1]
        self.assertTrue(call_kwargs.get("delete"))
        mock_deprecation.assert_any_call(
            "--with-delete", self.create_command.WITH_DELETE_DEPRECATION_MSG
        )

    @mock.patch("dcmanagerclient.utils.print_deprecation_notice")
    def test_create_strategy_with_deprecated_delete_only(self, mock_deprecation):
        """Test --delete-only maps to --cleanup and prints deprecation notice"""
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        strategy = utils.make_strategy(
            strategy_type=expected_strategy_type,
            extra_args={
                "release_id": None,
                "snapshot": False,
                "rollback": False,
                "delete": False,
                "cleanup": True,
                "kube_upgrade": "",
            },
        )
        manager_to_test.create_sw_update_strategy.return_value = strategy

        self.call(self.create_command, ["subcloud1", "--delete-only"])

        call_kwargs = manager_to_test.create_sw_update_strategy.call_args[1]
        self.assertTrue(call_kwargs.get("cleanup"))
        mock_deprecation.assert_any_call(
            "--delete-only", self.create_command.DELETE_ONLY_DEPRECATION_MSG
        )
