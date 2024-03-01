#
# Copyright (c) 2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.api.v1.alarm_manager import AlarmSummary
from dcmanagerclient.commands.v1 import alarm_manager as alarm_cmd
from dcmanagerclient.tests import base

FAKE_MANAGER = None
FAKE_NAME = "subcloud1"
FAKE_CRITICAL = "0"
FAKE_MAJOR = "1"
FAKE_MINOR = "0"
FAKE_WARNINGS = "0"
FAKE_STATUS = "degraded"

ALARM_SUMMARY = AlarmSummary(
    FAKE_MANAGER,
    FAKE_NAME,
    FAKE_CRITICAL,
    FAKE_MAJOR,
    FAKE_MINOR,
    FAKE_WARNINGS,
    FAKE_STATUS,
)


class TestCLIAlarmSummaryV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        # The client is the alarm_manager
        self.client = self.app.client_manager.alarm_manager

    def test_list_alarm_summary(self):
        self.client.list_alarms.return_value = [ALARM_SUMMARY]
        actual_call = self.call(alarm_cmd.ListAlarmSummary)
        self.assertEqual(
            [
                (
                    FAKE_NAME,
                    FAKE_CRITICAL,
                    FAKE_MAJOR,
                    FAKE_MINOR,
                    FAKE_WARNINGS,
                    FAKE_STATUS,
                )
            ],
            actual_call[1],
        )
