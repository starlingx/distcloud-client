#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import sw_patch_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1 import utils
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin


class TestPatchUpdateStrategy(UpdateStrategyMixin, base.BaseCommandTest):

    def setUp(self):
        super().setUp()

        # Increase results_length due to the 'upload only' field
        self.results_length += 1

        self.sw_update_manager = (
            self.app.client_manager.sw_patch_manager.sw_patch_manager
        )
        self.create_command = cli_cmd.CreatePatchUpdateStrategy
        self.show_command = cli_cmd.ShowPatchUpdateStrategy
        self.delete_command = cli_cmd.DeletePatchUpdateStrategy
        self.apply_command = cli_cmd.ApplyPatchUpdateStrategy
        self.abort_command = cli_cmd.AbortPatchUpdateStrategy

    def test_create_strategy_upload_only(self):
        """Test that a strategy can be created with the --upload-only option"""

        # prepare mixin attributes
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=expected_strategy_type, extra_args={"upload-only": True}
        )

        # mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.create_command, ["--upload-only"])

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

        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(fields[-4], "upload only")
        self.assertEqual(results[-4], True)
