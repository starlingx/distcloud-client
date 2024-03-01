#
# Copyright (c) 2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.api.v1.sw_update_options_manager import SwUpdateOptions
from dcmanagerclient.commands.v1 import (
    sw_update_options_manager as sw_update_options_cmd,
)
from dcmanagerclient.tests import base

FAKE_MANAGER = None
FAKE_CLOUD = "1"
FAKE_STORAGE_APPLY_TYPE = "parallel"
NEW_FAKE_STORAGE_APPLY_TYPE = "serial"
FAKE_WORKER_APPLY_TYPE = "serial"
FAKE_MAX_PARALLEL = "5"
FAKE_ALARM_RESTRICTIONS = "strict"
FAKE_DEFAULT_INSTANCE_ACTION = "migrate"
FAKE_CREATED_AT = None
FAKE_UPDATED_AT = None

SW_UPDATE_OPTION = SwUpdateOptions(
    FAKE_MANAGER,
    FAKE_CLOUD,
    FAKE_STORAGE_APPLY_TYPE,
    FAKE_WORKER_APPLY_TYPE,
    FAKE_MAX_PARALLEL,
    FAKE_ALARM_RESTRICTIONS,
    FAKE_DEFAULT_INSTANCE_ACTION,
    FAKE_CREATED_AT,
    FAKE_UPDATED_AT,
)

UPDATED_SW_UPDATE_OPTION = SwUpdateOptions(
    FAKE_MANAGER,
    FAKE_CLOUD,
    NEW_FAKE_STORAGE_APPLY_TYPE,
    FAKE_WORKER_APPLY_TYPE,
    FAKE_MAX_PARALLEL,
    FAKE_ALARM_RESTRICTIONS,
    FAKE_DEFAULT_INSTANCE_ACTION,
    FAKE_CREATED_AT,
    FAKE_UPDATED_AT,
)


class TestCLISWUpdateOptionsManagerV1(base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        # The client is the subcloud_group_manager
        self.client = self.app.client_manager.sw_update_options_manager

    def test_list_sw_update_options(self):
        self.client.sw_update_options_list.return_value = [SW_UPDATE_OPTION]
        actual_call = self.call(sw_update_options_cmd.ListSwUpdateOptions)
        self.assertEqual(
            [
                (
                    FAKE_CLOUD,
                    FAKE_STORAGE_APPLY_TYPE,
                    FAKE_WORKER_APPLY_TYPE,
                    FAKE_MAX_PARALLEL,
                    FAKE_ALARM_RESTRICTIONS,
                    FAKE_DEFAULT_INSTANCE_ACTION,
                )
            ],
            actual_call[1],
        )

    def test_list_sw_update_options_empty(self):
        self.client.sw_update_options_list.return_value = []
        actual_call = self.call(sw_update_options_cmd.ListSwUpdateOptions)
        self.assertEqual(
            (("<none>", "<none>", "<none>", "<none>", "<none>", "<none>"),),
            actual_call[1],
        )

    def test_show_sw_update_options_default(self):
        self.client.sw_update_options_detail.return_value = [SW_UPDATE_OPTION]
        actual_call = self.call(sw_update_options_cmd.ShowSwUpdateOptions)
        self.assertEqual(
            (
                FAKE_CLOUD,
                FAKE_STORAGE_APPLY_TYPE,
                FAKE_WORKER_APPLY_TYPE,
                FAKE_MAX_PARALLEL,
                FAKE_ALARM_RESTRICTIONS,
                FAKE_DEFAULT_INSTANCE_ACTION,
                FAKE_CREATED_AT,
                FAKE_UPDATED_AT,
            ),
            actual_call[1],
        )

    def test_show_sw_update_options_by_ref(self):
        self.client.sw_update_options_detail.return_value = [SW_UPDATE_OPTION]
        actual_call = self.call(
            sw_update_options_cmd.ShowSwUpdateOptions, app_args=[FAKE_CLOUD]
        )
        self.assertEqual(
            (
                FAKE_CLOUD,
                FAKE_STORAGE_APPLY_TYPE,
                FAKE_WORKER_APPLY_TYPE,
                FAKE_MAX_PARALLEL,
                FAKE_ALARM_RESTRICTIONS,
                FAKE_DEFAULT_INSTANCE_ACTION,
                FAKE_CREATED_AT,
                FAKE_UPDATED_AT,
            ),
            actual_call[1],
        )

    def test_update_sw_update_options(self):
        self.client.sw_update_options_update.return_value = [UPDATED_SW_UPDATE_OPTION]
        actual_call = self.call(
            sw_update_options_cmd.UpdateSwUpdateOptions,
            app_args=[
                "--storage-apply-type=" + NEW_FAKE_STORAGE_APPLY_TYPE,
                "--worker-apply-type=" + FAKE_WORKER_APPLY_TYPE,
                "--max-parallel-workers=" + FAKE_MAX_PARALLEL,
                "--alarm-restriction-type=" + FAKE_ALARM_RESTRICTIONS,
                "--default-instance-action=" + FAKE_DEFAULT_INSTANCE_ACTION,
            ],
        )
        self.assertEqual(
            (
                FAKE_CLOUD,
                NEW_FAKE_STORAGE_APPLY_TYPE,
                FAKE_WORKER_APPLY_TYPE,
                FAKE_MAX_PARALLEL,
                FAKE_ALARM_RESTRICTIONS,
                FAKE_DEFAULT_INSTANCE_ACTION,
                FAKE_CREATED_AT,
                FAKE_UPDATED_AT,
            ),
            actual_call[1],
        )

    def test_delete_sw_update_options_by_ref(self):
        self.call(sw_update_options_cmd.DeleteSwUpdateOptions, app_args=[FAKE_CLOUD])
        self.client.sw_update_options_delete.assert_called_once_with(FAKE_CLOUD)

    def test_delete_sw_update_options_without_ref(self):
        self.assertRaises(
            SystemExit,
            self.call,
            sw_update_options_cmd.DeleteSwUpdateOptions,
            app_args=[],
        )
