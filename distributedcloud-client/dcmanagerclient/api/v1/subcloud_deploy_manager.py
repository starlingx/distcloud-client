# Copyright (c) 2020-2024 Wind River Systems, Inc.
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
    resource_name = "subcloud_deploy"

    def __init__(
        self,
        deploy_playbook=None,
        deploy_overrides=None,
        deploy_chart=None,
        prestage_images=None,
        software_version=None,
    ):
        self.deploy_playbook = deploy_playbook
        self.deploy_overrides = deploy_overrides
        self.deploy_chart = deploy_chart
        self.prestage_images = prestage_images
        self.software_version = software_version


class SubcloudDeployManager(base.ResourceManager):
    resource_class = SubcloudDeploy

    def _process_json_response(self, json_object):
        resource = []
        deploy_playbook = json_object.get("deploy_playbook")
        deploy_overrides = json_object.get("deploy_overrides")
        deploy_chart = json_object.get("deploy_chart")
        prestage_images = json_object.get("prestage_images")
        software_version = json_object.get("software_version")

        resource.append(
            self.resource_class(
                deploy_playbook,
                deploy_overrides,
                deploy_chart,
                prestage_images,
                software_version,
            )
        )

        return resource

    def _subcloud_deploy_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_object = json_response_key["subcloud_deploy"]
        resource = self._process_json_response(json_object)
        return resource

    def _deploy_upload(self, url, files, data):
        fields = {}
        for k, v in files.items():
            with open(v, "rb") as file:
                fields.update({k: (v, file.read())})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}
        resp = self.http_client.post(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = self._process_json_response(json_object)
        return resource

    def _deploy_delete(self, url):
        resp = self.http_client.delete(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)

    def subcloud_deploy_show(self, release):
        url = "/subcloud-deploy/"
        if release:
            url += release
        return self._subcloud_deploy_detail(url)

    def subcloud_deploy_upload(self, **kwargs):
        files = kwargs.get("files")
        data = kwargs.get("data")
        url = "/subcloud-deploy/"
        return self._deploy_upload(url, files, data)

    def subcloud_deploy_delete(self, release, **kwargs):
        url = "/subcloud-deploy/"
        data = kwargs.get("data")
        if release:
            url += release + "/"
        url += "?deployment_files=" + data["deployment_files"]
        url += "&prestage_images=" + data["prestage_images"]
        return self._deploy_delete(url)
