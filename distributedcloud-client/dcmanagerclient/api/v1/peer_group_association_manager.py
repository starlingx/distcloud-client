#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json

OPTION_NOT_APPLICABLE = "Not applicable"
SYNC_STATUS_INVALID = "invalid"
BASE_URL = "/peer-group-associations/"


class PeerGroupAssociation(base.Resource):
    resource_name = "peer_group_association"

    def __init__(
        self,
        manager,
        association_id,
        peer_group_id,
        system_peer_id,
        peer_group_priority,
        association_type,
        sync_status,
        sync_message,
        created_at,
        updated_at,
    ):
        self.manager = manager
        self.association_id = association_id
        self.peer_group_id = peer_group_id
        self.system_peer_id = system_peer_id
        self.peer_group_priority = peer_group_priority
        self.association_type = association_type
        self.sync_status = sync_status
        self.sync_message = sync_message
        self.created_at = created_at
        self.updated_at = updated_at


class peer_group_association_manager(base.ResourceManager):
    resource_class = PeerGroupAssociation

    def _json_to_resource(self, json_object):
        sync_message = (
            None
            if "sync-message" not in json_object
            else json_object["sync-message"]
        )
        return self.resource_class(
            self,
            association_id=json_object["id"],
            peer_group_id=json_object["peer-group-id"],
            system_peer_id=json_object["system-peer-id"],
            peer_group_priority=json_object["peer-group-priority"],
            association_type=json_object["association-type"],
            sync_status=json_object["sync-status"],
            sync_message=sync_message,
            created_at=json_object["created-at"],
            updated_at=json_object["updated-at"],
        )

    def _peer_group_association_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = [self._json_to_resource(json_object)]
        return resource

    def peer_group_association_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["peer_group_associations"]
        resource = list()
        for json_object in json_objects:
            resource.append(self._json_to_resource(json_object))
        return resource

    def peer_group_association_sync(self, url):
        resp = self.http_client.patch(url, {})
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = [self._json_to_resource(json_object)]
        return resource

    def peer_group_association_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = [self._json_to_resource(json_object)]
        return resource

    def peer_group_association_update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = [self._json_to_resource(json_object)]
        return resource

    def add_peer_group_association(self, **kwargs):
        data = kwargs
        url = BASE_URL
        return self.peer_group_association_create(url, data)

    def list_peer_group_associations(self):
        url = BASE_URL
        return self.peer_group_association_list(url)

    def peer_group_association_detail(self, associate_ref):
        url = BASE_URL + associate_ref
        return self._peer_group_association_detail(url)

    def sync_peer_group_association(self, associate_ref):
        url = BASE_URL + f"{associate_ref}/sync"
        return self.peer_group_association_sync(url)

    def delete_peer_group_association(self, peer_id):
        url = BASE_URL + peer_id
        return self._delete(url)

    def update_peer_group_association(self, peer_id, **kwargs):
        data = kwargs
        url = BASE_URL + peer_id
        return self.peer_group_association_update(url, data)
