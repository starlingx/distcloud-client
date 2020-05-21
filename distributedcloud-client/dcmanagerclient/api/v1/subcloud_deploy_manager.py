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
# Copyright (c) 2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

from requests_toolbelt import MultipartEncoder

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SubcloudDeploy(base.Resource):
    resource_name = 'subcloud_deploy'

    def __init__(self, deploy_playbook, deploy_overrides, deploy_chart):
        self.deploy_playbook = deploy_playbook
        self.deploy_overrides = deploy_overrides
        self.deploy_chart = deploy_chart


class subcloud_deploy_manager(base.ResourceManager):
    resource_class = SubcloudDeploy

    def _subcloud_deploy_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_object = json_response_key['subcloud_deploy']
        resource = list()
        resource.append(
            self.resource_class(
                deploy_playbook=json_object['deploy_playbook'],
                deploy_overrides=json_object['deploy_overrides'],
                deploy_chart=json_object['deploy_chart']))
        return resource

    def _deploy_upload(self, url, data):
        fields = dict()
        for k, v in data.items():
            fields.update({k: (v, open(v, 'rb'),)})
        enc = MultipartEncoder(fields=fields)
        headers = {'Content-Type': enc.content_type}
        resp = self.http_client.post(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                deploy_playbook=json_object['deploy_playbook'],
                deploy_overrides=json_object['deploy_overrides'],
                deploy_chart=json_object['deploy_chart']))
        return resource

    def subcloud_deploy_show(self):
        url = '/subcloud-deploy/'
        return self._subcloud_deploy_detail(url)

    def subcloud_deploy_upload(self, **kwargs):
        data = kwargs
        url = '/subcloud-deploy/'
        return self._deploy_upload(url, data)
