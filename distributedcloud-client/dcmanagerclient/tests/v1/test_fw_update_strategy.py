#
# Copyright (c) 2020-2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import fw_update_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin


class TestFwUpdateStrategy(UpdateStrategyMixin, base.BaseCommandTest):
    def setUp(self):
        super().setUp()
        self.sw_update_manager = self.app.client_manager.fw_update_manager
        self.create_command = cli_cmd.CreateFwUpdateStrategy
        self.show_command = cli_cmd.ShowFwUpdateStrategy
        self.delete_command = cli_cmd.DeleteFwUpdateStrategy
        self.apply_command = cli_cmd.ApplyFwUpdateStrategy
        self.abort_command = cli_cmd.AbortFwUpdateStrategy
