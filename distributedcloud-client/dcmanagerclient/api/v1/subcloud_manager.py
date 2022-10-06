# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2022 Wind River Systems, Inc.
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

from requests_toolbelt import MultipartEncoder

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class subcloud_manager(base.ResourceManager):
    resource_class = base.Subcloud

    def json_to_resource(self, json_object):
        return self.resource_class(
            self,
            subcloud_id=json_object['id'],
            name=json_object['name'],
            description=json_object['description'],
            location=json_object['location'],
            software_version=json_object['software-version'],
            management_state=json_object['management-state'],
            availability_status=json_object['availability-status'],
            deploy_status=json_object['deploy-status'],
            error_description=json_object['error-description'],
            management_subnet=json_object['management-subnet'],
            management_start_ip=json_object['management-start-ip'],
            management_end_ip=json_object['management-end-ip'],
            management_gateway_ip=json_object['management-gateway-ip'],
            systemcontroller_gateway_ip=json_object[
                'systemcontroller-gateway-ip'],
            created_at=json_object['created-at'],
            updated_at=json_object['updated-at'],
            group_id=json_object['group_id'],
            backup_status=json_object['backup-status'],
            backup_datetime=json_object['backup-datetime'])

    def subcloud_create(self, url, body, data):
        fields = dict()
        for k, v in body.items():
            fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self.http_client.post(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_update(self, url, body, data):
        fields = dict()
        if body is not None:
            for k, v in body.items():
                fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self.http_client.patch(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_reconfigure(self, url, body, data):
        fields = dict()
        for k, v in body.items():
            fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self.http_client.patch(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_reinstall(self, url, body, data):
        fields = dict()
        for k, v in body.items():
            fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self.http_client.patch(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_restore(self, url, body, data):
        fields = dict()
        for k, v in body.items():
            fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self.http_client.patch(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def _subcloud_prestage(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
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
                    deploy_status=json_object['deploy-status'],
                    error_description=json_object['error-description'],
                    management_subnet=json_object['management-subnet'],
                    management_start_ip=json_object['management-start-ip'],
                    management_end_ip=json_object['management-end-ip'],
                    management_gateway_ip=json_object['management-gateway-ip'],
                    systemcontroller_gateway_ip=json_object[
                        'systemcontroller-gateway-ip'],
                    created_at=json_object['created-at'],
                    updated_at=json_object['updated-at'],
                    group_id=json_object['group_id'],
                    sync_status=json_object['sync_status'],
                    endpoint_sync_status=json_object['endpoint_sync_status'],
                    backup_status=json_object['backup-status'],
                    backup_datetime=json_object['backup-datetime']))
        return resource

    def _subcloud_detail(self, url, detail=None):
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
                deploy_status=json_object['deploy-status'],
                error_description=json_object['error-description'],
                management_subnet=json_object['management-subnet'],
                management_start_ip=json_object['management-start-ip'],
                management_end_ip=json_object['management-end-ip'],
                management_gateway_ip=json_object['management-gateway-ip'],
                systemcontroller_gateway_ip=json_object[
                    'systemcontroller-gateway-ip'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at'],
                group_id=json_object['group_id'],
                endpoint_sync_status=json_object['endpoint_sync_status'],
                backup_status=json_object['backup-status'],
                backup_datetime=json_object['backup-datetime']))
        if detail is not None:
            resource[0].oam_floating_ip = json_object['oam_floating_ip']
        return resource

    def add_subcloud(self, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        url = '/subclouds/'
        return self.subcloud_create(url, files, data)

    def list_subclouds(self):
        url = '/subclouds/'
        return self.subcloud_list(url)

    def subcloud_additional_details(self, subcloud_ref):
        url = '/subclouds/%s/detail' % subcloud_ref
        return self._subcloud_detail(url, True)

    def subcloud_detail(self, subcloud_ref):
        url = '/subclouds/%s' % subcloud_ref
        return self._subcloud_detail(url)

    def delete_subcloud(self, subcloud_ref):
        url = '/subclouds/%s' % subcloud_ref
        return self._delete(url)

    def prestage_subcloud(self, subcloud_ref, **kwargs):
        data = kwargs.get('data')
        url = '/subclouds/%s/prestage' % subcloud_ref
        return self._subcloud_prestage(url, data)

    def update_subcloud(self, subcloud_ref, **kwargs):
        files = kwargs.get('files')
        data = kwargs.get('data')
        url = '/subclouds/%s' % subcloud_ref
        return self.subcloud_update(url, files, data)

    def reconfigure_subcloud(self, subcloud_ref, **kwargs):
        files = kwargs.get('files')
        data = kwargs.get('data')
        url = '/subclouds/%s/reconfigure' % subcloud_ref
        return self.subcloud_reconfigure(url, files, data)

    def reinstall_subcloud(self, subcloud_ref, **kwargs):
        files = kwargs.get('files')
        data = kwargs.get('data')
        url = '/subclouds/%s/reinstall' % subcloud_ref
        return self.subcloud_reinstall(url, files, data)

    def restore_subcloud(self, subcloud_ref, **kwargs):
        files = kwargs.get('files')
        data = kwargs.get('data')
        url = '/subclouds/%s/restore' % subcloud_ref
        return self.subcloud_restore(url, files, data)
