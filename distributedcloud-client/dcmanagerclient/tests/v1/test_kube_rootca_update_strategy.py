#
# Copyright (c) 2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import kube_rootca_update_manager as cli_cmd
from dcmanagerclient.tests import base
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
