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
            alarms.name if alarms.name else '-',
            alarms.critical if int(alarms.critical) >= 0 else '-',
            alarms.major if int(alarms.major) >= 0 else '-',
            alarms.minor if int(alarms.minor) >= 0 else '-',
            alarms.warnings if int(alarms.warnings) >= 0 else '-',
            alarms.status
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class ListAlarmSummary(base.DCManagerLister):
    """List alarm summaries of subclouds."""

    def _get_format_function(self):
        return format

    def get_parser(self, prog_name):
        parser = super(ListAlarmSummary, self).get_parser(prog_name)
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.alarm_manager
        return dcmanager_client.alarm_manager.list_alarms()
