#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#


from dcmanagerclient.commands.v1 import sw_patch_manager as cli_cmd
from dcmanagerclient.exceptions import DCManagerClientException
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1 import utils
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin


class TestPatchUpdateStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()

        # Increase results_length due to the 'upload only' field
        self.results_length += 1

        self.sw_update_manager = self.app.client_manager.sw_patch_manager
        self.create_command = cli_cmd.CreatePatchUpdateStrategy
        self.show_command = cli_cmd.ShowPatchUpdateStrategy
        self.delete_command = cli_cmd.DeletePatchUpdateStrategy
        self.apply_command = cli_cmd.ApplyPatchUpdateStrategy
        self.abort_command = cli_cmd.AbortPatchUpdateStrategy

        # prepare mixin attributes
        self.manager_to_test = self.sw_update_manager
        self.expected_strategy_type = self.manager_to_test.update_type

    def test_create_strategy(self):
        """Test that a strategy needs a patch_id option"""

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=self.expected_strategy_type,
            extra_args={"patch_id": "stx-10.1"},
        )

        self.manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Assert raises Exception for API call without required parameter
        self.assertRaises(SystemExit, self.call, self.create_command, [])

        # Assert call will not raise Exception for API call with required parameter
        try:
            self.call(self.create_command, ["stx-10.1"])
        except Exception:
            self.fail("Unexpected Exception raised")

    def test_create_strategy_upload_only(self):
        """Test that a strategy can be created with the --upload-only option"""

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=self.expected_strategy_type,
            extra_args={"upload-only": True, "patch_id": "stx-10.1"},
        )

        # mock that there is no pre-existing strategy
        self.manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.create_command, ["stx-10.1", "--upload-only"])

        # results is a tuple of expected length
        self.assertEqual(len(results), self.results_length)
        # result tuple values are
        # - strategy type
        # - subcloud apply type
        # - max parallel subclouds
        # - stop on failure
        # - upload only
        # - state
        # - created_at
        # - updated_at

        self.assertEqual(results[0], self.expected_strategy_type)
        self.assertEqual(fields[-4], "upload only")
        self.assertEqual(results[-4], True)

    def test_create_strategy_remove(self):
        """Test that a strategy can be created with the --remove option"""

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=self.expected_strategy_type,
            extra_args={"remove": True, "patch_id": "stx-10.1"},
        )

        # mock that there is no pre-existing strategy
        self.manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        _, results = self.call(self.create_command, ["stx-10.1", "--remove"])

        self.assertEqual(len(results), self.results_length)
        self.assertEqual(results[0], self.expected_strategy_type)

    def test_create_strategy_upload_only_and_remove(self):
        """Test that a strategy can be created with the --remove option"""

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=self.expected_strategy_type,
            extra_args={"upload-only": True, "remove": True, "patch_id": "stx-10.1"},
        )

        # mock that there is no pre-existing strategy
        self.manager_to_test.create_sw_update_strategy.return_value = strategy

        self.assertRaises(
            DCManagerClientException,
            self.call,
            self.create_command,
            ["stx-10.1", "--upload-only", "--remove"],
        )
