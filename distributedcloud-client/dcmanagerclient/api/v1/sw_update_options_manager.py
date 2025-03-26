# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017, 2019, 2021, 2024-2025 Wind River Systems, Inc.
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

DEFAULT_REGION_NAME = "SystemController"


class SwUpdateOptions(base.Resource):
    resource_name = "sw_update_options"

    def __init__(
        self,
        manager,
        cloud,
        storage_apply_type,
        worker_apply_type,
        max_parallel_workers,
        alarm_restriction_type,
        default_instance_action,
        created_at,
        updated_at,
    ):
        self.manager = manager
        self.cloud = cloud
        self.storage_apply_type = storage_apply_type
        self.worker_apply_type = worker_apply_type
        self.max_parallel_workers = max_parallel_workers
        self.alarm_restriction_type = alarm_restriction_type
        self.default_instance_action = default_instance_action
        self.created_at = created_at
        self.updated_at = updated_at


class SwUpdateOptionsManager(base.ResourceManager):
    resource_class = SwUpdateOptions

    def sw_update_options_update(self, subcloud_ref, **kwargs):
        data = kwargs
        if subcloud_ref:
            url = f"/sw-update-options/{subcloud_ref}"
        else:
            url = f"/sw-update-options/{DEFAULT_REGION_NAME}"
        return self._sw_update_options_update(url, data)

    def sw_update_options_list(self):
        url = "/sw-update-options"
        return self._sw_update_options_list(url)

    def sw_update_options_detail(self, subcloud_ref):
        if subcloud_ref:
            url = f"/sw-update-options/{subcloud_ref}"
        else:
            url = f"/sw-update-options/{DEFAULT_REGION_NAME}"
        return self._sw_update_options_detail(url)

    def sw_update_options_delete(self, subcloud_ref):
        if subcloud_ref:
            url = f"/sw-update-options/{subcloud_ref}"
        else:
            url = f"/sw-update-options/{DEFAULT_REGION_NAME}"
        return self._sw_update_options_delete(url)

    def _sw_update_options_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(
            self.resource_class(
                self,
                cloud=json_object["name"],
                storage_apply_type=json_object["storage-apply-type"],
                worker_apply_type=json_object["worker-apply-type"],
                max_parallel_workers=json_object["max-parallel-workers"],
                alarm_restriction_type=json_object["alarm-restriction-type"],
                default_instance_action=json_object["default-instance-action"],
                created_at=json_object["created-at"],
                updated_at=json_object["updated-at"],
            )
        )
        return resource

    def _sw_update_options_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key["sw-update-options"]
        resource = []
        for json_object in json_objects:
            resource.append(
                self.resource_class(
                    self,
                    cloud=json_object["name"],
                    storage_apply_type=json_object["storage-apply-type"],
                    worker_apply_type=json_object["worker-apply-type"],
                    max_parallel_workers=json_object["max-parallel-workers"],
                    alarm_restriction_type=json_object["alarm-restriction-type"],
                    default_instance_action=json_object["default-instance-action"],
                    created_at=json_object["created-at"],
                    updated_at=json_object["updated-at"],
                )
            )
        return resource

    def _sw_update_options_delete(self, url):
        resp = self.http_client.delete(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)

    def _sw_update_options_update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(
            self.resource_class(
                self,
                cloud=json_object["name"],
                storage_apply_type=json_object["storage-apply-type"],
                worker_apply_type=json_object["worker-apply-type"],
                max_parallel_workers=json_object["max-parallel-workers"],
                alarm_restriction_type=json_object["alarm-restriction-type"],
                default_instance_action=json_object["default-instance-action"],
                created_at=json_object["created-at"],
                updated_at=json_object["updated-at"],
            )
        )
        return resource
