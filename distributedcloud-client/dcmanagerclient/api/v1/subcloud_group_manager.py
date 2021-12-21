# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2020-2021 Wind River Systems, Inc.
# All Rights Reserved.
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

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SubcloudGroup(base.Resource):
    resource_name = 'subcloud_group'

    def __init__(self,
                 manager,
                 group_id,
                 name,
                 description,
                 update_apply_type,
                 max_parallel_subclouds,
                 created_at,
                 updated_at):
        self.manager = manager
        self.group_id = group_id
        self.name = name
        self.description = description
        self.update_apply_type = update_apply_type
        self.max_parallel_subclouds = max_parallel_subclouds
        self.created_at = created_at
        self.updated_at = updated_at


class subcloud_group_manager(base.ResourceManager):
    resource_class = SubcloudGroup

    def __init__(self, http_client, subcloud_manager):
        super(subcloud_group_manager, self).__init__(http_client)
        self.subcloud_manager = subcloud_manager

    def _json_to_resource(self, json_object):
        return self.resource_class(
            self,
            group_id=json_object['id'],
            name=json_object['name'],
            description=json_object['description'],
            update_apply_type=json_object['update_apply_type'],
            max_parallel_subclouds=json_object['max_parallel_subclouds'],
            created_at=json_object['created-at'],
            updated_at=json_object['updated-at'])

    def subcloud_group_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self._json_to_resource(json_object))
        return resource

    def subcloud_group_update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self._json_to_resource(json_object))
        return resource

    def subcloud_group_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key['subcloud_groups']
        resource = []
        for json_object in json_objects:
            resource.append(self._json_to_resource(json_object))
        return resource

    def _subcloud_group_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self._json_to_resource(json_object))
        return resource

    def _list_subclouds_for_subcloud_group(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key['subclouds']
        resource = []
        for json_object in json_objects:
            resource.append(
                self.subcloud_manager.json_to_resource(json_object))
        return resource

    def add_subcloud_group(self, **kwargs):
        data = kwargs
        url = '/subcloud-groups/'
        return self.subcloud_group_create(url, data)

    def list_subcloud_groups(self):
        url = '/subcloud-groups/'
        return self.subcloud_group_list(url)

    def subcloud_group_list_subclouds(self, subcloud_group_ref):
        url = '/subcloud-groups/%s/subclouds' % subcloud_group_ref
        return self._list_subclouds_for_subcloud_group(url)

    def subcloud_group_detail(self, subcloud_group_ref):
        url = '/subcloud-groups/%s' % subcloud_group_ref
        return self._subcloud_group_detail(url)

    def delete_subcloud_group(self, subcloud_group_ref):
        url = '/subcloud-groups/%s' % subcloud_group_ref
        return self._delete(url)

    def update_subcloud_group(self, subcloud_group_ref, **kwargs):
        data = kwargs
        url = '/subcloud-groups/%s' % subcloud_group_ref
        return self.subcloud_group_update(url, data)
