#
# Copyright (c) 2020-2021 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from dcmanagerclient.tests.v1 import utils


class UpdateStrategyMixin(object):
    """Mixin for testing the different types of dcmanager update strategies.

    Used by concrete testsuites of strategy types such as patch, upgrade, etc..
    Subclasses must:
     - mix with BaseCommandTest
     - provide: self.sw_update_manager
     - provide: self.create_command
     - provide: self.show_command
     - provide: self.delete_command
     - provide: self.apply_command
     - provide: self.abort_command
    """
    def setUp(self):
        super(UpdateStrategyMixin, self).setUp()

    def test_create_strategy(self):
        """Test that if no strategy exists, one can be created."""
        # prepare mixin attributes
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type

        # mock the result of the API call
        strategy = utils.make_strategy(strategy_type=expected_strategy_type)

        # mock that there is no pre-existing strategy
        manager_to_test.create_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.create_command)

        # results is a tuple of expected length 7
        self.assertEqual(len(results), 7)
        # result tuple values are
        # - strategy_type
        # - subcloud_apply_type
        # - max_parallel_subclouds
        # - stop_on_failure
        # - state
        # - created_at
        # - updated_at
        self.assertEqual(results[0], expected_strategy_type)

    def test_get_strategy(self):
        # prepare mocked results
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type
        expected_apply_type = 'parallel'
        strategy = utils.make_strategy(strategy_type=expected_strategy_type,
                                       subcloud_apply_type=expected_apply_type)
        manager_to_test.update_sw_strategy_detail.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.show_command)
        # results is a tuple of expected length 7
        self.assertEqual(len(results), 7)
        # result tuple values are
        # - strategy_type
        # - subcloud_apply_type
        # - max_parallel_subclouds
        # - stop_on_failure
        # - state
        # - created_at
        # - updated_at
        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(results[1], expected_apply_type)

    def test_apply_strategy(self):
        # prepare mocked results
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type
        expected_apply_type = 'parallel'
        strategy = utils.make_strategy(strategy_type=expected_strategy_type,
                                       subcloud_apply_type=expected_apply_type)
        manager_to_test.apply_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.apply_command)
        # results is a tuple of expected length 7
        self.assertEqual(len(results), 7)
        # result tuple values are
        # - strategy_type
        # - subcloud_apply_type
        # - max_parallel_subclouds
        # - stop_on_failure
        # - state
        # - created_at
        # - updated_at
        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(results[1], expected_apply_type)

    def test_abort_strategy(self):
        # prepare mocked results
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type
        expected_apply_type = 'parallel'
        strategy = utils.make_strategy(strategy_type=expected_strategy_type,
                                       subcloud_apply_type=expected_apply_type)
        manager_to_test.abort_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.abort_command)
        # results is a tuple of expected length 7
        self.assertEqual(len(results), 7)
        # result tuple values are
        # - strategy_type
        # - subcloud_apply_type
        # - max_parallel_subclouds
        # - stop_on_failure
        # - state
        # - created_at
        # - updated_at
        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(results[1], expected_apply_type)

    def test_delete_strategy(self):
        # prepare mocked results
        manager_to_test = self.sw_update_manager
        expected_strategy_type = manager_to_test.update_type
        expected_apply_type = 'parallel'
        strategy = utils.make_strategy(strategy_type=expected_strategy_type,
                                       subcloud_apply_type=expected_apply_type)
        manager_to_test.delete_sw_update_strategy.return_value = strategy

        # invoke the backend method for the CLI.
        # Returns a tuple of field descriptions, and a second tuple of values
        fields, results = self.call(self.delete_command)
        # results is a tuple of expected length 7
        self.assertEqual(len(results), 7)
        # result tuple values are
        # - strategy_type
        # - subcloud_apply_type
        # - max_parallel_subclouds
        # - stop_on_failure
        # - state
        # - created_at
        # - updated_at
        self.assertEqual(results[0], expected_strategy_type)
        self.assertEqual(results[1], expected_apply_type)
