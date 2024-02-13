# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json

BASE_URL = "/subcloud-peer-groups/"


class SubcloudPeerGroup(base.Resource):
    resource_name = "subcloud_peer_group"

    def __init__(
        self,
        manager,
        peer_group_id,
        peer_group_name,
        group_priority,
        group_state,
        system_leader_id,
        system_leader_name,
        max_subcloud_rehoming,
        created_at,
        updated_at,
    ):
        self.manager = manager
        self.id = peer_group_id
        self.peer_group_name = peer_group_name
        self.group_priority = group_priority

        self.group_state = group_state
        self.system_leader_id = system_leader_id
        self.system_leader_name = system_leader_name
        self.max_subcloud_rehoming = max_subcloud_rehoming
        self.created_at = created_at
        self.updated_at = updated_at


class subcloud_peer_group_manager(base.ResourceManager):
    resource_class = SubcloudPeerGroup

    def __init__(self, http_client, subcloud_manager):
        super(subcloud_peer_group_manager, self).__init__(http_client)
        self.subcloud_manager = subcloud_manager

    def json_to_resource(self, json_object):
        return self.resource_class(
            self,
            peer_group_id=json_object["id"],
            peer_group_name=json_object["peer_group_name"],
            group_priority=json_object["group_priority"],
            group_state=json_object["group_state"],
            system_leader_id=json_object["system_leader_id"],
            system_leader_name=json_object["system_leader_name"],
            max_subcloud_rehoming=json_object["max_subcloud_rehoming"],
            created_at=json_object["created-at"],
            updated_at=json_object["updated-at"],
        )

    def _subcloud_peer_group_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def _subcloud_peer_group_status(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(json_object)
        return resource

    def subcloud_peer_group_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_peer_group_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["subcloud_peer_groups"]
        resource = list()
        for json_object in json_objects:
            resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_peer_group_update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def _list_subclouds_for_subcloud_peer_group(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["subclouds"]
        resource = list()
        for json_object in json_objects:
            resource.append(self.subcloud_manager.json_to_resource(json_object))
        return resource

    def subcloud_peer_group_migrate(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["subclouds"]
        resource = list()
        for json_object in json_objects:
            resource.append(self.subcloud_manager.json_to_resource(json_object))
        return resource

    def add_subcloud_peer_group(self, **kwargs):
        data = kwargs
        url = BASE_URL
        return self.subcloud_peer_group_create(url, data)

    def delete_subcloud_peer_group(self, subcloud_peer_group_ref):
        url = BASE_URL + subcloud_peer_group_ref
        return self._delete(url)

    def subcloud_peer_group_detail(self, subcloud_peer_group_ref):
        url = BASE_URL + subcloud_peer_group_ref
        return self._subcloud_peer_group_detail(url)

    def list_subcloud_peer_groups(self):
        url = BASE_URL
        return self.subcloud_peer_group_list(url)

    def update_subcloud_peer_group(self, subcloud_peer_group_ref, **kwargs):
        data = kwargs
        url = BASE_URL + subcloud_peer_group_ref
        return self.subcloud_peer_group_update(url, data)

    def migrate_subcloud_peer_group(self, subcloud_peer_group_ref, **kwargs):
        data = kwargs
        url = BASE_URL + f"{subcloud_peer_group_ref}/migrate"
        return self.subcloud_peer_group_migrate(url, data)

    def subcloud_peer_group_list_subclouds(self, subcloud_peer_group_ref):
        url = BASE_URL + f"{subcloud_peer_group_ref}/subclouds"
        return self._list_subclouds_for_subcloud_peer_group(url)

    def subcloud_peer_group_status(self, subcloud_peer_group_ref):
        url = BASE_URL + f"{subcloud_peer_group_ref}/status"
        return self._subcloud_peer_group_status(url)
