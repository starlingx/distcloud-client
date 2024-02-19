#
# Copyright (c) 2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.api.v1.strategy_step_manager import StrategyStep
from dcmanagerclient.commands.v1 import sw_update_manager as sw_update_cmd
from dcmanagerclient.tests import base

FAKE_MANAGER = None
FAKE_CLOUD = "subcloud1"
FAKE_STAGE = "1"
FAKE_STATE = "initial"
FAKE_DETAILS = ""
FAKE_STARTED_AT = None
FAKE_FINISHED_AT = None
FAKE_CREATED_AT = None
FAKE_UPDATED_AT = None

STRATEGY_STEP = StrategyStep(
    FAKE_MANAGER,
    FAKE_CLOUD,
    FAKE_STAGE,
    FAKE_STATE,
    FAKE_DETAILS,
    FAKE_STARTED_AT,
    FAKE_FINISHED_AT,
    FAKE_CREATED_AT,
    FAKE_UPDATED_AT,
)


class TestCLISWUpdateManagerV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.client_manager.strategy_step_manager

    def test_show_sw_update_strategy_step(self):
        results = []
        results.append(STRATEGY_STEP)
        self.client.strategy_step_manager.strategy_step_detail.return_value = results
        actual_call = self.call(
            sw_update_cmd.ShowSwUpdateStrategyStep, app_args=[FAKE_CLOUD]
        )
        self.assertEqual(
            (
                FAKE_CLOUD,
                FAKE_STAGE,
                FAKE_STATE,
                FAKE_DETAILS,
                FAKE_STARTED_AT,
                FAKE_FINISHED_AT,
                FAKE_CREATED_AT,
                FAKE_UPDATED_AT,
            ),
            actual_call[1],
        )
