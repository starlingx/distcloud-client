# Copyright (c) 2017 Ericsson AB.
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

from dcmanagerclient.commands.v1 import base


def format(alarms=None):
    columns = (
        'NAME',
        'CRITICAL_ALARMS',
        'MAJOR_ALARMS',
        'MINOR_ALARMS',
        'WARNINGS',
        'STATUS'
    )

    if alarms:
        data = (
            alarms.name if alarms.name >= 0 else '-',
            alarms.critical if alarms.critical >= 0 else '-',
            alarms.major if alarms.major >= 0 else '-',
            alarms.minor if alarms.minor >= 0 else '-',
            alarms.warnings if alarms.warnings >= 0 else '-',
            alarms.status
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class ListAlarmSummary(base.DCManagerLister):
    """List alarm summaries of subclouds."""

    def _get_format_function(self):
        return format

    def get_parser(self, parsed_args):
        parser = super(ListAlarmSummary, self).get_parser(parsed_args)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.alarm_manager
        return dcmanager_client.alarm_manager.list_alarms()
