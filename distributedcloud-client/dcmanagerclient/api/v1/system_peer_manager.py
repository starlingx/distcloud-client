#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json

BASE_URL = "/system-peers/"


class SystemPeer(base.Resource):
    resource_name = "system_peer"

    def __init__(
        self,
        manager,
        peer_id,
        peer_uuid,
        peer_name,
        manager_endpoint,
        manager_username,
        peer_controller_gateway_address,
        administrative_state,
        heartbeat_interval,
        heartbeat_failure_threshold,
        heartbeat_failure_policy,
        heartbeat_maintenance_timeout,
        availability_state,
        created_at,
        updated_at,
    ):
        self.manager = manager
        self.peer_id = peer_id
        self.peer_uuid = peer_uuid
        self.peer_name = peer_name
        self.manager_endpoint = manager_endpoint
        self.manager_username = manager_username
        self.gateway_address = peer_controller_gateway_address
        self.administrative_state = administrative_state
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_failure_threshold = heartbeat_failure_threshold
        self.heartbeat_failure_policy = heartbeat_failure_policy
        self.heartbeat_maintenance_timeout = heartbeat_maintenance_timeout
        self.availability_state = availability_state
        self.created_at = created_at
        self.updated_at = updated_at


class system_peer_manager(base.ResourceManager):
    resource_class = SystemPeer

    def __init__(self, http_client, subcloud_peer_group_manager):
        super().__init__(http_client)
        self.subcloud_peer_group_manager = subcloud_peer_group_manager

    def _json_to_resource(self, json_object):
        return self.resource_class(
            self,
            peer_id=json_object["id"],
            peer_uuid=json_object["peer-uuid"],
            peer_name=json_object["peer-name"],
            manager_endpoint=json_object["manager-endpoint"],
            manager_username=json_object["manager-username"],
            peer_controller_gateway_address=json_object[
                "peer-controller-gateway-address"
            ],
            administrative_state=json_object["administrative-state"],
            heartbeat_interval=json_object["heartbeat-interval"],
            heartbeat_failure_threshold=json_object["heartbeat-failure-threshold"],
            heartbeat_failure_policy=json_object["heartbeat-failure-policy"],
            heartbeat_maintenance_timeout=json_object[
                "heartbeat-maintenance-timeout"
            ],
            availability_state=json_object["availability-state"],
            created_at=json_object["created-at"],
            updated_at=json_object["updated-at"],
        )

    def system_peer_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._json_to_resource(json_object))
        return resource

    def system_peer_update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._json_to_resource(json_object))
        return resource

    def system_peer_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["system_peers"]
        resource = []
        for json_object in json_objects:
            resource.append(self._json_to_resource(json_object))
        return resource

    def _system_peer_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._json_to_resource(json_object))
        return resource

    def _list_peer_groups_for_system_peer(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["subcloud_peer_groups"]
        resource = []
        for json_object in json_objects:
            resource.append(
                self.subcloud_peer_group_manager.json_to_resource(json_object)
            )
        return resource

    def add_system_peer(self, **kwargs):
        data = kwargs
        url = BASE_URL
        return self.system_peer_create(url, data)

    def list_system_peers(self):
        url = BASE_URL
        return self.system_peer_list(url)

    def system_peer_detail(self, system_peer_ref):
        url = BASE_URL + system_peer_ref
        return self._system_peer_detail(url)

    def delete_system_peer(self, system_peer_ref):
        url = BASE_URL + system_peer_ref
        return self._delete(url)

    def update_system_peer(self, system_peer_ref, **kwargs):
        data = kwargs
        url = BASE_URL + system_peer_ref
        return self.system_peer_update(url, data)

    def system_peer_list_peer_groups(self, system_peer_ref):
        url = f"{BASE_URL}{system_peer_ref}/subcloud-peer-groups"
        return self._list_peer_groups_for_system_peer(url)
