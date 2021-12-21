# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2021 Wind River Systems, Inc.
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
    def __init__(self, http_client, url='sw-update-strategy'):
        super(sw_strategy_manager, self).__init__(
            http_client,
            update_type=None)

        # Removing strategy type from base class parameters
        self.get_url = '/{url}'.format(url=url)
        self.delete_url = '/{url}'.format(url=url)
        self.actions_url = '/{url}/actions'.format(url=url)
