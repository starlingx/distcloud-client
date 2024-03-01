#
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import sw_deploy_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin
from dcmanagerclient.tests.v1 import utils


class TestSwDeployStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()

        # Increase results_length due to the 'upload only' field
        self.results_length += 1

        self.sw_update_manager = self.app.client_manager.sw_deploy_manager
        self.create_command = cli_cmd.CreateSwDeployStrategy
        self.show_command = cli_cmd.ShowSwDeployStrategy
        self.delete_command = cli_cmd.DeleteSwDeployStrategy
        self.apply_command = cli_cmd.ApplySwDeployStrategy
        self.abort_command = cli_cmd.AbortSwDeployStrategy

    def test_create_strategy(self):
        """Test deploy strategy should be created with release"""

        # prepare mixin attributes
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=expected_strategy_type,
            extra_args={"release": "stx-24.09.1"},
        )

        # mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.create_command, ["stx-24.09.1"])

        # results is a tuple of expected length
        self.assertEqual(len(results), self.results_length)
        # result tuple values are
        # - strategy type
        # - subcloud apply type
        # - max parallel subclouds
        # - stop on failure
        # - release_id
        # - state
        # - created_at
        # - updated_at
        failure_index = fields.index("stop on failure")
        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(fields[failure_index + 1], "release_id")
        self.assertEqual(results[failure_index + 1], "stx-24.09.1")

    def test_create_strategy_without_release_id(self):
        """Test deploy strategy should not be created without release"""

        # prepare mixin attributes
        manager_to_test = self.sw_update_manager

        # mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = None

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        self.assertRaises(SystemExit, self.call, self.create_command, [])
