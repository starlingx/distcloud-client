# Copyright (c) 2020-2022 Wind River Systems, Inc.
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

from requests_toolbelt import MultipartEncoder

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SubcloudDeploy(base.Resource):
    resource_name = 'subcloud_deploy'

    def __init__(self, deploy_playbook=None, deploy_overrides=None,
                 deploy_chart=None, prestage_images=None):
        self.deploy_playbook = deploy_playbook
        self.deploy_overrides = deploy_overrides
        self.deploy_chart = deploy_chart
        self.prestage_images = prestage_images


class subcloud_deploy_manager(base.ResourceManager):
    resource_class = SubcloudDeploy

    def _process_json_response(self, json_object):
        resource = list()
        deploy_playbook = json_object.get('deploy_playbook')
        deploy_overrides = json_object.get('deploy_overrides')
        deploy_chart = json_object.get('deploy_chart')
        prestage_images = json_object.get('prestage_images')

        resource.append(
            self.resource_class(deploy_playbook, deploy_overrides,
                                deploy_chart, prestage_images))

        return resource

    def _subcloud_deploy_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_object = json_response_key['subcloud_deploy']
        resource = self._process_json_response(json_object)
        return resource

    def _deploy_upload(self, url, data):
        fields = dict()
        for k, v in data.items():
            fields.update({k: (v, open(v, 'rb'),)})
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self.http_client.post(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = self._process_json_response(json_object)
        return resource

    def subcloud_deploy_show(self):
        url = '/subcloud-deploy/'
        return self._subcloud_deploy_detail(url)

    def subcloud_deploy_upload(self, **kwargs):
        data = kwargs
        url = '/subcloud-deploy/'
        return self._deploy_upload(url, data)
