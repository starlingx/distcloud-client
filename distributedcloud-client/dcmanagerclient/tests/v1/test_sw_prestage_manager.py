#
# Copyright (c) 2022 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import getpass
import mock

from dcmanagerclient.commands.v1 import sw_prestage_manager as cli_cmd
from dcmanagerclient.tests import base
from dcmanagerclient.tests.v1.mixins import UpdateStrategyMixin


class TestSwPrestageStrategy(UpdateStrategyMixin, base.BaseCommandTest):

    def setUp(self):
        super(TestSwPrestageStrategy, self).setUp()
        self.sw_update_manager = \
            self.app.client_manager.sw_prestage_manager.sw_prestage_manager

        p = mock.patch.object(getpass, 'getpass')
        self.mock_prompt = p.start()
        self.mock_prompt.return_value = str('testpassword')
        self.addCleanup(p.stop)

        self.create_command = cli_cmd.CreateSwPrestageStrategy
        self.show_command = cli_cmd.ShowSwPrestageStrategy
        self.delete_command = cli_cmd.DeleteSwPrestageStrategy
        self.apply_command = cli_cmd.ApplySwPrestageStrategy
        self.abort_command = cli_cmd.AbortSwPrestageStrategy
