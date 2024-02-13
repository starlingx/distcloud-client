# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2024 Wind River Systems, Inc.
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
        return self.resource_class.from_payload(self, json_object)

    def subcloud_create(self, url, body, data):
        fields = dict()
        for k, v in body.items():
            fields.update(
                {
                    k: (
                        v,
                        open(v, "rb"),
                    )
                }
            )
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}
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
                fields.update(
                    {
                        k: (
                            v,
                            open(v, "rb"),
                        )
                    }
                )
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}
        resp = self.http_client.patch(url, enc, headers=headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(self.json_to_resource(json_object))
        return resource

    def subcloud_redeploy(self, url, body, data):
        fields = dict()
        for k, v in body.items():
            fields.update(
                {
                    k: (
                        v,
                        open(v, "rb"),
                    )
                }
            )
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {"content-type": enc.content_type}
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
        if json_object.get("prestage_software_version"):
            resource[0].prestage_software_version = json_object[
                "prestage_software_version"
            ]
        return resource

    def subcloud_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["subclouds"]
        resource = self.resource_class.from_payloads(self, json_objects)
        return resource

    def _subcloud_detail(self, url, detail=None):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        subcloud = self.resource_class.from_payload(self, json_object)
        resource = [subcloud]
        if detail is not None:
            resource[0].oam_floating_ip = json_object["oam_floating_ip"]
            resource[0].deploy_config_sync_status = json_object[
                "deploy_config_sync_status"
            ]
        return resource

    def add_subcloud(self, **kwargs):
        data = kwargs.get("data")
        files = kwargs.get("files")
        url = "/subclouds/"
        return self.subcloud_create(url, files, data)

    def list_subclouds(self):
        url = "/subclouds/"
        return self.subcloud_list(url)

    def subcloud_additional_details(self, subcloud_ref):
        url = f"/subclouds/{subcloud_ref}/detail"
        return self._subcloud_detail(url, True)

    def subcloud_detail(self, subcloud_ref):
        url = f"/subclouds/{subcloud_ref}"
        return self._subcloud_detail(url)

    def delete_subcloud(self, subcloud_ref):
        url = f"/subclouds/{subcloud_ref}"
        return self._delete(url)

    def prestage_subcloud(self, subcloud_ref, **kwargs):
        data = kwargs.get("data")
        url = f"/subclouds/{subcloud_ref}/prestage"
        return self._subcloud_prestage(url, data)

    def update_subcloud(self, subcloud_ref, **kwargs):
        files = kwargs.get("files")
        data = kwargs.get("data")
        url = f"/subclouds/{subcloud_ref}"
        return self.subcloud_update(url, files, data)

    def redeploy_subcloud(self, subcloud_ref, **kwargs):
        files = kwargs.get("files")
        data = kwargs.get("data")
        url = f"/subclouds/{subcloud_ref}/redeploy"
        return self.subcloud_redeploy(url, files, data)
