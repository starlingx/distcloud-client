#
# Copyright (c) 2020-2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import kube_upgrade_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin


class TestKubeUpgradeStrategy(UpdateStrategyMixin, base.BaseCommandTest):

    def setUp(self):
        super().setUp()
        self.sw_update_manager = (
            self.app.client_manager.kube_upgrade_manager.kube_upgrade_manager
        )
        self.create_command = cli_cmd.CreateKubeUpgradeStrategy
        self.show_command = cli_cmd.ShowKubeUpgradeStrategy
        self.delete_command = cli_cmd.DeleteKubeUpgradeStrategy
        self.apply_command = cli_cmd.ApplyKubeUpgradeStrategy
        self.abort_command = cli_cmd.AbortKubeUpgradeStrategy
