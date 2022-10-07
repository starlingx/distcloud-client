
#
# Copyright (c) 2022 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class subcloud_backup_manager(base.ResourceManager):

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

    def subcloud_backup_create(self, url, body, data):
        if body:
            data.update(body)
        enc = json.dumps(data)
        headers = {'Content-Type': 'application/json'}

        resp = self.http_client.post(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key['subclouds']
        resource = []
        for json_object in json_objects:
            resource.append(
                self.json_to_resource(json_object))
        return resource

    def subcloud_backup_delete(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.patch(url, data)
        if resp.status_code not in {204, 207}:
            self._raise_api_exception(resp)
        elif resp.status_code == 207:
            return json.loads(resp.content)
        return None

    def backup_subcloud_create(self, **kwargs):
        files = kwargs.get('files')
        data = kwargs.get('data')
        url = '/subcloud-backup/'
        return self.subcloud_backup_create(url, files, data)

    def backup_subcloud_delete(self, release_version, **kwargs):
        data = kwargs.get('data')
        url = '/subcloud-backup/delete/%s' % release_version
        return self.subcloud_backup_delete(url, data)
