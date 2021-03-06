# Copyright (c) 2017 Ericsson AB.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Copyright (c) 2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import mock

from oslo_utils import timeutils

from dcmanagerclient.api.v1.strategy_step_manager import StrategyStep
from dcmanagerclient.commands.v1 import sw_update_manager as cli_cmd
from dcmanagerclient.tests import base

TEST_CLOUD_ID = 1
TEST_STAGE = 1
TEST_STATE = 'initializing'
TEST_DETAILS = 'some details'
TIME_NOW = timeutils.utcnow().isoformat()
TEST_STARTED_AT = TIME_NOW
TEST_FINISHED_AT = TIME_NOW
TEST_CREATED_AT = TIME_NOW
TEST_UPDATED_AT = TIME_NOW


class TestCLI(base.BaseCommandTest):

    def setUp(self):
        super(TestCLI, self).setUp()

    def test_list_strategy_steps(self):
        sample_step = StrategyStep(mock,
                                   TEST_CLOUD_ID,
                                   TEST_STAGE,
                                   TEST_STATE,
                                   TEST_DETAILS,
                                   TEST_STARTED_AT,
                                   TEST_FINISHED_AT,
                                   TEST_CREATED_AT,
                                   TEST_UPDATED_AT)
        results = []
        results.append(sample_step)
        self.app.client_manager.strategy_step_manager.strategy_step_manager.\
            list_strategy_steps.return_value = results

        actual_call = self.call(cli_cmd.ListSwUpdateStrategyStep)
        # ListStrategyStep returns a tuple, want the second field of the tuple
        result_steps = actual_call[1]
        # Only 1 step
        self.assertEqual(1, len(result_steps))
        # The step object is a tuple based on the formatter
        for step in result_steps:
            self.assertEqual(TEST_CLOUD_ID, step[0])
