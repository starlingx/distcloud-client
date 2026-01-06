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

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SwUpdateStrategy(base.Resource):
    resource_name = "sw_update_strategy"

    def __init__(
        self,
        manager,
        strategy_type,
        subcloud_apply_type,
        max_parallel_subclouds,
        stop_on_failure,
        state,
        created_at,
        updated_at,
        extra_args=None,
    ):
        self.manager = manager
        self.strategy_type = strategy_type
        self.subcloud_apply_type = subcloud_apply_type
        self.max_parallel_subclouds = max_parallel_subclouds
        self.stop_on_failure = stop_on_failure
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at
        self.extra_args = extra_args


class SwUpdateManager(base.ResourceManager):
    """SwUpdateManager

    sw_update_manager is an abstract class that is used by subclasses to
    manage API actions for specific update strategy types  such as software
    patches and firmware updates.
    """

    def __init__(
        self,
        http_client,
        update_type,
        resource_class=SwUpdateStrategy,
        url="sw-update-strategy",
        extra_args=None,
    ):
        super().__init__(http_client)
        self.resource_class = resource_class
        self.update_type = update_type
        # create_url is typically /<foo>/
        self.create_url = f"/{url}/"
        # get_url is typically /<foo>
        self.get_url = f"/{url}?type={update_type}"
        # delete_url is typically /<foo> (same as get)
        self.delete_url = f"/{url}?type={update_type}"
        # actions_url is typically /<foo>/actions
        self.actions_url = f"/{url}/actions?type={update_type}"

        if extra_args is None:
            self.extra_args = []
        else:
            self.extra_args = extra_args

    def create_sw_update_strategy(self, **kwargs):
        data = kwargs
        if self.update_type is not None:
            data.update({"type": self.update_type})
        return self._sw_update_create(self.create_url, data)

    def update_sw_strategy_detail(self):
        return self._sw_update_detail(self.get_url)

    def delete_sw_update_strategy(self):
        return self._sw_update_delete(self.delete_url)

    def apply_sw_update_strategy(self):
        data = {"action": "apply"}
        return self._sw_update_action(self.actions_url, data)

    def abort_sw_update_strategy(self):
        data = {"action": "abort"}
        return self._sw_update_action(self.actions_url, data)

    def extract_extra_args(self, json_object):
        args_dict = {}

        for x in self.extra_args:
            json_extra_args = json_object.get("extra-args")
            if json_extra_args:
                arg = json_extra_args.get(x)
                # Check for not None, not empty string, and handle boolean False
                if arg is not None and str(arg).strip() != "":
                    args_dict[x] = arg
        if args_dict:
            return args_dict
        return None

    def _build_from_json(self, json_object):
        return self.resource_class(
            self,
            strategy_type=json_object["type"],
            subcloud_apply_type=json_object["subcloud-apply-type"],
            max_parallel_subclouds=json_object["max-parallel-subclouds"],
            stop_on_failure=json_object["stop-on-failure"],
            state=json_object["state"],
            created_at=json_object["created-at"],
            updated_at=json_object["updated-at"],
            extra_args=self.extract_extra_args(json_object),
        )

    def _sw_update_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._build_from_json(json_object))
        return resource

    def _sw_update_delete(self, url):
        resp = self.http_client.delete(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._build_from_json(json_object))
        return resource

    def _sw_update_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._build_from_json(json_object))
        return resource

    def _sw_update_action(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self._build_from_json(json_object))
        return resource
