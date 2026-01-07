#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SubcloudBackupConfigManager(base.ResourceManager):
    """Manager for subcloud backup configuration operations"""

    resource_class = base.Resource

    def subcloud_backup_config_show(self):
        url = "/subcloud-backup-config"

        resp = self.http_client.get(url)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return get_json(resp)

    def subcloud_backup_config_update(self, **kwargs):
        url = "/subcloud-backup-config"

        data = {}
        if "storage_location" in kwargs:
            data["storage_location"] = kwargs["storage_location"]
        if "retention_count" in kwargs:
            data["retention_count"] = kwargs["retention_count"]

        if not data:
            raise ValueError("At least one parameter must be provided")

        resp = self.http_client.patch(url, json.dumps(data))

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        return get_json(resp)
