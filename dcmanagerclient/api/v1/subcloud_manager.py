# Copyright (c) 2017 Ericsson AB.
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
# Copyright (c) 2017 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class Subcloud(base.Resource):
    resource_name = 'subclouds'

    def __init__(self, manager, subcloud_id, name, description, location,
                 software_version, management_state, availability_status,
                 management_subnet, management_start_ip, management_end_ip,
                 management_gateway_ip, systemcontroller_gateway_ip,
                 created_at, updated_at, sync_status="unknown",
                 endpoint_sync_status={}):
        self.manager = manager
        self.subcloud_id = subcloud_id
        self.name = name
        self.description = description
        self.location = location
        self.software_version = software_version
        self.management_subnet = management_subnet
        self.management_state = management_state
        self.availability_status = availability_status
        self.management_start_ip = management_start_ip
        self.management_end_ip = management_end_ip
        self.management_gateway_ip = management_gateway_ip
        self.systemcontroller_gateway_ip = systemcontroller_gateway_ip
        self.created_at = created_at
        self.updated_at = updated_at
        self.sync_status = sync_status
        self.endpoint_sync_status = endpoint_sync_status


class subcloud_manager(base.ResourceManager):
    resource_class = Subcloud

    def subcloud_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_id=json_object['id'],
                name=json_object['name'],
                description=json_object['description'],
                location=json_object['location'],
                software_version=json_object['software-version'],
                management_state=json_object['management-state'],
                availability_status=json_object['availability-status'],
                management_subnet=json_object['management-subnet'],
                management_start_ip=json_object['management-start-ip'],
                management_end_ip=json_object['management-end-ip'],
                management_gateway_ip=json_object['management-gateway-ip'],
                systemcontroller_gateway_ip=json_object[
                    'systemcontroller-gateway-ip'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at']))
        return resource

    def subcloud_update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_id=json_object['id'],
                name=json_object['name'],
                description=json_object['description'],
                location=json_object['location'],
                software_version=json_object['software-version'],
                management_state=json_object['management-state'],
                availability_status=json_object['availability-status'],
                management_subnet=json_object['management-subnet'],
                management_start_ip=json_object['management-start-ip'],
                management_end_ip=json_object['management-end-ip'],
                management_gateway_ip=json_object['management-gateway-ip'],
                systemcontroller_gateway_ip=json_object[
                    'systemcontroller-gateway-ip'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at']))
        return resource

    def subcloud_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key['subclouds']
        resource = []
        for json_object in json_objects:
            resource.append(
                self.resource_class(
                    self,
                    subcloud_id=json_object['id'],
                    name=json_object['name'],
                    description=json_object['description'],
                    location=json_object['location'],
                    software_version=json_object['software-version'],
                    management_state=json_object['management-state'],
                    availability_status=json_object['availability-status'],
                    management_subnet=json_object['management-subnet'],
                    management_start_ip=json_object['management-start-ip'],
                    management_end_ip=json_object['management-end-ip'],
                    management_gateway_ip=json_object['management-gateway-ip'],
                    systemcontroller_gateway_ip=json_object[
                        'systemcontroller-gateway-ip'],
                    created_at=json_object['created-at'],
                    updated_at=json_object['updated-at'],
                    sync_status=json_object['sync_status'],
                    endpoint_sync_status=json_object['endpoint_sync_status']))
        return resource

    def _subcloud_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_id=json_object['id'],
                name=json_object['name'],
                description=json_object['description'],
                location=json_object['location'],
                software_version=json_object['software-version'],
                management_state=json_object['management-state'],
                availability_status=json_object['availability-status'],
                management_subnet=json_object['management-subnet'],
                management_start_ip=json_object['management-start-ip'],
                management_end_ip=json_object['management-end-ip'],
                management_gateway_ip=json_object['management-gateway-ip'],
                systemcontroller_gateway_ip=json_object[
                    'systemcontroller-gateway-ip'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at'],
                endpoint_sync_status=json_object['endpoint_sync_status']))
        return resource

    def subcloud_generate_config(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        return json_object['config']

    def add_subcloud(self, **kwargs):
        data = kwargs
        url = '/subclouds/'
        return self.subcloud_create(url, data)

    def list_subclouds(self):
        url = '/subclouds/'
        return self.subcloud_list(url)

    def subcloud_detail(self, subcloud_ref):
        url = '/subclouds/%s' % subcloud_ref
        return self._subcloud_detail(url)

    def delete_subcloud(self, subcloud_ref):
        url = '/subclouds/%s' % subcloud_ref
        return self._delete(url)

    def update_subcloud(self, subcloud_ref, **kwargs):
        data = kwargs
        url = '/subclouds/%s' % subcloud_ref
        return self.subcloud_update(url, data)

    def generate_config_subcloud(self, subcloud_ref, **kwargs):
        data = kwargs
        url = '/subclouds/%s/config' % subcloud_ref
        return self.subcloud_generate_config(url, data)
