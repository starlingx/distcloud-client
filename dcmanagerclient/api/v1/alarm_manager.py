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

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json


class AlarmSumary(base.Resource):
    resource_name = 'alarms'

    def __init__(self, manager, name, critical, major,
                 minor, warnings, status):
        self.manger = manager
        self.name = name
        self.critical = critical
        self.major = major
        self.minor = minor
        self.warnings = warnings
        self.status = status


class alarm_manager(base.ResourceManager):
    resource_class = AlarmSumary

    def alarm_summary_list(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = json_response_key['alarm_summary']
        resource = []
        for json_object in json_objects:
            resource.append(
                self.resource_class(
                    self,
                    name=json_object['region_name'],
                    critical=json_object['critical_alarms'],
                    major=json_object['major_alarms'],
                    minor=json_object['minor_alarms'],
                    warnings=json_object['warnings'],
                    status=json_object['cloud_status']))
        return resource

    def list_alarms(self):
        url = '/alarms/'
        return self.alarm_summary_list(url)
