#
# Copyright (c) 2021, 2024,2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import kube_rootca_update_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1 import utils
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin


class TestKubeRootcaUpdateStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.sw_update_manager = self.app.client_manager.kube_rootca_update_manager
        self.create_command = cli_cmd.CreateKubeRootcaUpdateStrategy
        self.show_command = cli_cmd.ShowKubeRootcaUpdateStrategy
        self.delete_command = cli_cmd.DeleteKubeRootcaUpdateStrategy
        self.apply_command = cli_cmd.ApplyKubeRootcaUpdateStrategy
        self.abort_command = cli_cmd.AbortKubeRootcaUpdateStrategy

    def test_create_strategy_with_algorithm_and_key_size(self):
        manager = self.sw_update_manager
        manager.create_sw_update_strategy.return_value = utils.make_strategy(
            strategy_type=manager.update_type
        )

        self.call(self.create_command, ["--algorithm", "ECDSA", "--key-size", "521"])

        call_kwargs = manager.create_sw_update_strategy.call_args[1]
        self.assertEqual(call_kwargs["algorithm"], "ECDSA")
        self.assertEqual(call_kwargs["key-size"], 521)

    def test_create_strategy_without_algorithm_and_key_size(self):
        manager = self.sw_update_manager
        manager.create_sw_update_strategy.return_value = utils.make_strategy(
            strategy_type=manager.update_type
        )

        self.call(self.create_command)

        call_kwargs = manager.create_sw_update_strategy.call_args[1]
        self.assertNotIn("algorithm", call_kwargs)
        self.assertNotIn("key-size", call_kwargs)

    def test_create_strategy_with_invalid_algorithm(self):
        self.assertRaises(
            SystemExit, self.call, self.create_command, ["--algorithm", "DSA"]
        )

    def test_create_strategy_with_non_numeric_key_size(self):
        self.assertRaises(
            SystemExit, self.call, self.create_command, ["--key-size", "big"]
        )
