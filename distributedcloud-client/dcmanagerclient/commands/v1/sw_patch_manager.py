# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2021 Wind River Systems, Inc.
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
from dcmanagerclient.commands.v1 import sw_update_manager


class SwPatchManagerMixin(object):
    """This Mixin provides the update manager used for sw patch."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.sw_patch_manager
        return dcmanager_client.sw_patch_manager


class CreatePatchUpdateStrategy(SwPatchManagerMixin,
                                sw_update_manager.CreateSwUpdateStrategy):
    """Create a patch update strategy."""
    pass


class ShowPatchUpdateStrategy(SwPatchManagerMixin,
                              sw_update_manager.ShowSwUpdateStrategy):
    """Show the details of a patch update strategy for a subcloud."""
    pass


class DeletePatchUpdateStrategy(SwPatchManagerMixin,
                                sw_update_manager.DeleteSwUpdateStrategy):
    """Delete patch update strategy from the database."""
    pass


class ApplyPatchUpdateStrategy(SwPatchManagerMixin,
                               sw_update_manager.ApplySwUpdateStrategy):
    """Apply a patch update strategy."""
    pass


class AbortPatchUpdateStrategy(SwPatchManagerMixin,
                               sw_update_manager.AbortSwUpdateStrategy):
    """Abort a patch update strategy."""
    pass
