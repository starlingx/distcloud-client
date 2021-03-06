# Copyright (c) 2017 Ericsson AB.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
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
from dcmanagerclient.commands.v1 import sw_update_manager


class SwUpgradeManagerMixin(object):
    """This Mixin provides the update manager used for software upgrades."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.sw_upgrade_manager
        return dcmanager_client.sw_upgrade_manager


class CreateSwUpgradeStrategy(SwUpgradeManagerMixin,
                              sw_update_manager.CreateSwUpdateStrategy):
    """Create a software upgrade strategy."""
    pass


class ShowSwUpgradeStrategy(SwUpgradeManagerMixin,
                            sw_update_manager.ShowSwUpdateStrategy):
    """Show the details of a software upgrade strategy for a subcloud."""
    pass


class DeleteSwUpgradeStrategy(SwUpgradeManagerMixin,
                              sw_update_manager.DeleteSwUpdateStrategy):
    """Delete software upgrade strategy from the database."""
    pass


class ApplySwUpgradeStrategy(SwUpgradeManagerMixin,
                             sw_update_manager.ApplySwUpdateStrategy):
    """Apply a software upgrade strategy."""
    pass


class AbortSwUpgradeStrategy(SwUpgradeManagerMixin,
                             sw_update_manager.AbortSwUpdateStrategy):
    """Abort a software upgrade strategy."""
    pass
