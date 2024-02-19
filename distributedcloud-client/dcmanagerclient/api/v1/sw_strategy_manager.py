# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2021-2024 Wind River Systems, Inc.
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
from dcmanagerclient.api.v1.sw_update_manager import sw_update_manager


class sw_strategy_manager(sw_update_manager):
    def __init__(self, http_client, url="sw-update-strategy"):
        super().__init__(http_client, update_type=None)

        # Removing strategy type from base class parameters
        self.get_url = f"/{url}"
        self.delete_url = f"/{url}"
        self.actions_url = f"/{url}/actions"

    def extract_extra_args(self, json_object):
        # Since this generic strategy manager can interact with any strategy
        # type, it overrides extract_extra_args method of the sw_update_manager
        # class to return all extra-args without filtering by type so they are
        # available to the caller
        extra_args = json_object.get("extra-args")
        if extra_args:
            return extra_args
        return None
