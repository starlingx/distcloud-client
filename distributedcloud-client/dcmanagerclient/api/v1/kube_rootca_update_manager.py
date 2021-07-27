#
# Copyright (c) 2021 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from dcmanagerclient.api.v1.sw_update_manager import sw_update_manager

SW_UPDATE_TYPE_KUBE_ROOTCA_UPDATE = "kube-rootca-update"


class kube_rootca_update_manager(sw_update_manager):

    def __init__(self, http_client):
        super(kube_rootca_update_manager, self).__init__(
            http_client,
            update_type=SW_UPDATE_TYPE_KUBE_ROOTCA_UPDATE)
