#
# Copyright (c) 2022-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import getpass

import mock

from dcmanagerclient.commands.v1 import sw_prestage_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1 import utils
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin

FAKE_RELEASE = "21.12"


class TestSwPrestageStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.sw_update_manager = self.app.client_manager.sw_prestage_manager

        p = mock.patch.object(getpass, "getpass")
        self.mock_prompt = p.start()
        self.mock_prompt.return_value = str("testpassword")
        self.addCleanup(p.stop)

        self.create_command = cli_cmd.CreateSwPrestageStrategy
        self.show_command = cli_cmd.ShowSwPrestageStrategy
        self.delete_command = cli_cmd.DeleteSwPrestageStrategy
        self.apply_command = cli_cmd.ApplySwPrestageStrategy
        self.abort_command = cli_cmd.AbortSwPrestageStrategy

    def test_create_strategy_with_release_option(self):
        """Test that a strategy can be created with the --release option"""

        # prepare mixin attributes
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        # mock the result of the API call
        strategy = utils.make_strategy(
            strategy_type=expected_strategy_type,
            extra_args={"prestage-software-version": FAKE_RELEASE},
        )

        # mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.create_command, ["--release", FAKE_RELEASE])

        # results is a tuple of expected length
        self.assertEqual(len(results), self.results_length + 1)
        # result tuple values are
        # - strategy type
        # - subcloud apply type
        # - max parallel subclouds
        # - stop on failure
        # - prestage software version
        # - state
        # - created_at
        # - updated_at

        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(fields[-4], "prestage software version")
        self.assertEqual(results[-4], FAKE_RELEASE)
