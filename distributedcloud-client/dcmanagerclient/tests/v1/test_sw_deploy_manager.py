#
# Copyright (c) 2024-2025 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.commands.v1 import sw_deploy_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin
from dcmanagerclient.tests.v1 import utils

RELEASE_ID = "stx-10.01.100"


class TestSwDeployStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()

        # Increase results_length due to extra_args fields
        # This includes release_id, snapshot, rollback, and delete_option
        self.results_length += 4

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
        with_delete=False,
        delete_only=False,
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
                "with_delete": with_delete,
                "delete_only": delete_only,
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
        if with_delete:
            values.append("--with-delete")
        if delete_only:
            values.append("--delete-only")
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
        # - with_delete
        # - delete_only
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
        self.assertEqual(call_kwargs.get("with_delete", False), with_delete)
        self.assertEqual(call_kwargs.get("delete_only", False), delete_only)

    def base_create_strategy_failure(
        self,
        error_msg,
        release_id=None,
        snapshot=False,
        rollback=False,
        with_delete=False,
        delete_only=False,
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
        if with_delete:
            values.append("--with-delete")
        if delete_only:
            values.append("--delete-only")

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

    def test_create_strategy_with_delete(self):
        """Test deploy strategy created with delete enabled"""
        self.base_create_strategy_successful(release_id=RELEASE_ID, with_delete=True)

    def test_create_strategy_with_delete_only(self):
        """Test deploy strategy created with delete_only enabled"""
        self.base_create_strategy_successful(delete_only=True)

    def test_create_strategy_with_snapshot_and_with_delete(self):
        """Test deploy strategy created with snapshot and with_delete enabled"""
        self.base_create_strategy_successful(
            release_id=RELEASE_ID, snapshot=True, with_delete=True
        )

    def test_create_strategy_with_rollback(self):
        """Test deploy strategy created with rollback enabled"""
        self.base_create_strategy_successful(rollback=True)

    def test_create_strategy_without_release_id(self):
        """Test deploy strategy cannot created without release_id"""

        error_msg = "The --release-id is required to create a deploy strategy."
        self.base_create_strategy_failure(error_msg)

    def test_create_strategy_with_snapshot_and_rollback(self):
        """Test deploy strategy cannot created with snapshot and rollback"""
        error_msg = (
            "Option --snapshot cannot be used with any of the following "
            "options: --rollback or --delete-only."
        )
        self.base_create_strategy_failure(
            error_msg, release_id=RELEASE_ID, snapshot=True, rollback=True
        )

    def test_create_strategy_with_snapshot_and_delete_only(self):
        """Test deploy strategy cannot created with snapshot and delete_only"""
        error_msg = (
            "Option --snapshot cannot be used with any of the following "
            "options: --rollback or --delete-only."
        )
        self.base_create_strategy_failure(
            error_msg,
            release_id=RELEASE_ID,
            snapshot=True,
            delete_only=True,
        )

    def test_create_strategy_with_rollback_and_release_id(self):
        """Test deploy strategy cannot created with rollback and release_id"""
        error_msg = (
            "Option --rollback cannot be used with any of the following "
            "options: release-id, --snapshot, --with-delete or --delete-only."
        )
        self.base_create_strategy_failure(
            error_msg,
            release_id=RELEASE_ID,
            rollback=True,
        )

    def test_create_strategy_with_rollback_and_with_delete(self):
        """Test deploy strategy cannot created with rollback and with_delete"""
        error_msg = (
            "Option --rollback cannot be used with any of the following "
            "options: release-id, --snapshot, --with-delete or --delete-only."
        )
        self.base_create_strategy_failure(error_msg, rollback=True, with_delete=True)

    def test_create_strategy_with_rollback_and_delete_only(self):
        """Test deploy strategy cannot created with rollback and delete_only"""
        error_msg = (
            "Option --rollback cannot be used with any of the following "
            "options: release-id, --snapshot, --with-delete or --delete-only."
        )
        self.base_create_strategy_failure(error_msg, rollback=True, delete_only=True)

    def test_create_strategy_with_with_delete_and_delete_only(self):
        """Test deploy strategy cannot created with with_delete and delete_only"""
        error_msg = (
            "Option --with-delete cannot be used with any of the following "
            "options: --rollback or --delete-only."
        )
        self.base_create_strategy_failure(
            error_msg, release_id=RELEASE_ID, with_delete=True, delete_only=True
        )

    def test_create_strategy_with_delete_only_and_release_id(self):
        """Test deploy strategy cannot created with delete_only and release_id"""
        error_msg = (
            "Option --delete-only cannot be used with any of the following "
            "options: release-id, --snapshot, --rollback or --with-delete."
        )
        self.base_create_strategy_failure(
            error_msg, release_id=RELEASE_ID, delete_only=True
        )
