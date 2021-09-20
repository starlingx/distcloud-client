#
# Copyright (c) 2021 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from dcmanagerclient.commands.v1 import sw_update_manager


class KubeRootcaUpdateManagerMixin(object):
    """This Mixin provides the update manager used for kube rootca updates."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.kube_rootca_update_manager
        return dcmanager_client.kube_rootca_update_manager


class CreateKubeRootcaUpdateStrategy(KubeRootcaUpdateManagerMixin,
                                     sw_update_manager.CreateSwUpdateStrategy):
    """Create a kube rootca update strategy."""

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        """Disable validation the force option. Allows multiple subclouds."""
        pass


class ShowKubeRootcaUpdateStrategy(KubeRootcaUpdateManagerMixin,
                                   sw_update_manager.ShowSwUpdateStrategy):
    """Show the details of a kube rootca update strategy for a subcloud."""
    pass


class DeleteKubeRootcaUpdateStrategy(KubeRootcaUpdateManagerMixin,
                                     sw_update_manager.DeleteSwUpdateStrategy):
    """Delete kube rootca update strategy from the database."""
    pass


class ApplyKubeRootcaUpdateStrategy(KubeRootcaUpdateManagerMixin,
                                    sw_update_manager.ApplySwUpdateStrategy):
    """Apply a kube rootca update strategy."""
    pass


class AbortKubeRootcaUpdateStrategy(KubeRootcaUpdateManagerMixin,
                                    sw_update_manager.AbortSwUpdateStrategy):
    """Abort a kube rootca update strategy."""
    pass
