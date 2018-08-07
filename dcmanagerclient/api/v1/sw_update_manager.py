# Copyright (c) 2017 Ericsson AB.
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
# Copyright (c) 2017 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import json

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class SwUpdateStrategy(base.Resource):
    resource_name = 'sw_update_strategy'

    def __init__(self, manager, subcloud_apply_type, max_parallel_subclouds,
                 stop_on_failure, state,
                 created_at, updated_at):
        self.manager = manager
        self.subcloud_apply_type = subcloud_apply_type
        self.max_parallel_subclouds = max_parallel_subclouds
        self.stop_on_failure = stop_on_failure
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at


class StrategyStep(base.Resource):
    resource_name = 'strategy_step'

    def __init__(self, manager, cloud, stage, state, details,
                 started_at, finished_at, created_at, updated_at):
        self.manager = manager
        self.cloud = cloud
        self.stage = stage
        self.state = state
        self.details = details
        self.started_at = started_at
        self.finished_at = finished_at
        self.created_at = created_at
        self.updated_at = updated_at


class sw_update_manager(base.ResourceManager):
    resource_class = SwUpdateStrategy

    def create_patch_strategy(self, **kwargs):
        data = kwargs
        data.update({'type': 'patch'})
        url = '/sw-update-strategy/'
        return self.sw_update_create(url, data)

    def patch_strategy_detail(self):
        url = '/sw-update-strategy'
        return self.sw_update_detail(url)

    def delete_patch_strategy(self):
        url = '/sw-update-strategy'
        return self.sw_update_delete(url)

    def apply_patch_strategy(self):
        data = {'action': 'apply'}
        url = '/sw-update-strategy/actions'
        return self.sw_update_action(url, data)

    def abort_patch_strategy(self):
        data = {'action': 'abort'}
        url = '/sw-update-strategy/actions'
        return self.sw_update_action(url, data)

    def sw_update_create(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_apply_type=json_object['subcloud-apply-type'],
                max_parallel_subclouds=json_object['max-parallel-subclouds'],
                stop_on_failure=json_object['stop-on-failure'],
                state=json_object['state'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at']))
        return resource

    def sw_update_delete(self, url):
        resp = self.http_client.delete(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_apply_type=json_object['subcloud-apply-type'],
                max_parallel_subclouds=json_object['max-parallel-subclouds'],
                stop_on_failure=json_object['stop-on-failure'],
                state=json_object['state'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at']))
        return resource

    def sw_update_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_apply_type=json_object['subcloud-apply-type'],
                max_parallel_subclouds=json_object['max-parallel-subclouds'],
                stop_on_failure=json_object['stop-on-failure'],
                state=json_object['state'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at']))
        return resource

    def sw_update_action(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.post(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                subcloud_apply_type=json_object['subcloud-apply-type'],
                max_parallel_subclouds=json_object['max-parallel-subclouds'],
                stop_on_failure=json_object['stop-on-failure'],
                state=json_object['state'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at']))
        return resource


class strategy_step_manager(base.ResourceManager):
    resource_class = StrategyStep

    def list_strategy_steps(self):
        url = '/sw-update-strategy/steps'
        return self.strategy_step_list(url)

    def strategy_step_detail(self, cloud_name):
        url = '/sw-update-strategy/steps/%s' % cloud_name
        return self._strategy_step_detail(url)

    def strategy_step_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key['strategy-steps']
        resource = []
        for json_object in json_objects:
            resource.append(
                self.resource_class(
                    self,
                    cloud=json_object['cloud'],
                    stage=json_object['stage'],
                    state=json_object['state'],
                    details=json_object['details'],
                    started_at=json_object['started-at'],
                    finished_at=json_object['finished-at'],
                    created_at=json_object['created-at'],
                    updated_at=json_object['updated-at'],
                ))
        return resource

    def _strategy_step_detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = list()
        resource.append(
            self.resource_class(
                self,
                cloud=json_object['cloud'],
                stage=json_object['stage'],
                state=json_object['state'],
                details=json_object['details'],
                started_at=json_object['started-at'],
                finished_at=json_object['finished-at'],
                created_at=json_object['created-at'],
                updated_at=json_object['updated-at'],
            ))
        return resource
