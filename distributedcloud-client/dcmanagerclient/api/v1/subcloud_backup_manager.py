
#
# Copyright (c) 2022 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from requests_toolbelt import MultipartEncoder

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
        fields = dict()
        for k, v in body.items():
            fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'Content-Type': enc.content_type}
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

    def backup_subcloud_create(self, **kwargs):
        files = kwargs.get('files')
        data = kwargs.get('data')
        url = '/subcloud-backup/'
        return self.subcloud_backup_create(url, files, data)
