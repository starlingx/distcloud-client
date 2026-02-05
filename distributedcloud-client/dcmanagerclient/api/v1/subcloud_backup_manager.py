#
# Copyright (c) 2022, 2024-2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import json
from typing import Optional

from requests_toolbelt import MultipartEncoder

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SubcloudBackupManager(base.ResourceManager):
    resource_class = base.Subcloud

    def json_to_resource(self, json_object):
        return self.resource_class.from_payload(self, json_object)

    def subcloud_backup_create(self, url, files, data):
        fields = {}
        if files:
            for k, v in files.items():
                with open(v, "rb") as file:
                    fields.update({k: (v, file.read())})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}
        resp = self.http_client.post(url, enc, headers=headers)

        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["subclouds"]
        resource = []
        for json_object in json_objects:
            resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_backup_delete(self, url, data):
        fields = {}
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}

        resp = self.http_client.patch(url, enc, headers=headers)
        if resp.status_code not in {204, 207}:
            self._raise_api_exception(resp)
        elif resp.status_code == 207:
            return json.loads(resp.content)
        return None

    def subcloud_backup_restore(self, url, files, data):
        fields = {}
        if files:
            for k, v in files.items():
                with open(v, "rb") as file:
                    fields.update({k: (v, file.read())})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}

        resp = self.http_client.patch(url, enc, headers=headers)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        json_response_key = get_json(resp)
        json_objects = json_response_key["subclouds"]
        resource = []
        for json_object in json_objects:
            resource.append(self.json_to_resource(json_object))
        return resource

    def backup_subcloud_create(self, **kwargs):
        files = kwargs.get("files")
        data = kwargs.get("data")
        url = "/subcloud-backup/"
        return self.subcloud_backup_create(url, files, data)

    def backup_subcloud_delete(self, release_version, **kwargs):
        data = kwargs.get("data")
        url = f"/subcloud-backup/delete/{release_version}"
        return self.subcloud_backup_delete(url, data)

    def backup_subcloud_restore(self, **kwargs):
        files = kwargs.get("files")
        data = kwargs.get("data")
        url = "/subcloud-backup/restore"
        return self.subcloud_backup_restore(url, files, data)

    def subcloud_backup_list(
        self,
        subcloud: Optional[str] = None,
        group: Optional[str] = None,
        release: Optional[str] = None,
        storage: Optional[str] = None,
    ) -> list[dict]:
        """List subcloud backups with optional filters.

        :param subcloud: Subcloud name or ID to filter by
        :param group: Group name or ID to filter by
        :param release: Release version to filter by
        :param storage: Storage location to filter by
        :returns list: List of backup dictionaries
        """
        url = "/subcloud-backup"

        params = []
        if subcloud:
            params.append(f"subcloud={subcloud}")
        if group:
            params.append(f"group={group}")
        if release:
            params.append(f"release={release}")
        if storage:
            params.append(f"storage={storage}")

        if params:
            url += "?" + "&".join(params)

        resp = self.http_client.get(url)

        if resp.status_code != 200:
            self._raise_api_exception(resp)

        json_response = get_json(resp)
        backups = json_response.get("backups", [])

        return backups
