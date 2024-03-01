# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2021, 2024 Wind River Systems, Inc.
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
from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class StrategyStep(base.Resource):
    resource_name = "strategy_step"

    def __init__(
        self,
        manager,
        cloud,
        stage,
        state,
        details,
        started_at,
        finished_at,
        created_at,
        updated_at,
    ):
        self.manager = manager
        self.cloud = cloud
        self.stage = stage
        self.state = state
        self.details = details
        self.started_at = started_at
        self.finished_at = finished_at
        self.created_at = created_at
        self.updated_at = updated_at


class StrategyStepManager(base.ResourceManager):
    def __init__(self, http_client):
        super().__init__(http_client)
        self.resource_class = StrategyStep
        self.steps_url = "/sw-update-strategy/steps"
        self.response_key = "strategy-steps"

    def list_strategy_steps(self):
        return self._strategy_step_list(self.steps_url)

    def strategy_step_detail(self, cloud_name):
        url = f"{self.steps_url}/{cloud_name}"
        return self._strategy_step_detail(url)

    def build_from_json(self, json_object):
        return self.resource_class(
            self,
            cloud=json_object["cloud"],
            stage=json_object["stage"],
            state=json_object["state"],
            details=json_object["details"],
            started_at=json_object["started-at"],
            finished_at=json_object["finished-at"],
            created_at=json_object["created-at"],
            updated_at=json_object["updated-at"],
        )

    def _strategy_step_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key[self.response_key]
        resource = []
        for json_object in json_objects:
            resource.append(self.build_from_json(json_object))
        return resource

    def _strategy_step_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = []
        resource.append(self.build_from_json(json_object))
        return resource
