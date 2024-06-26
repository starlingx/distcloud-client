#
# Copyright (c) 2021, 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from dcmanagerclient.api.v1.sw_update_manager import SwUpdateManager

SW_UPDATE_TYPE_KUBE_ROOTCA_UPDATE = "kube-rootca-update"


class KubeRootcaUpdateManager(SwUpdateManager):
    def __init__(self, http_client):
        super().__init__(http_client, update_type=SW_UPDATE_TYPE_KUBE_ROOTCA_UPDATE)
        self.extra_args = ["subject", "expiry-date", "cert-file"]
