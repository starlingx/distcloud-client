# Copyright (c) 2022 Wind River Systems, Inc.
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

import base64

from dcmanagerclient.commands.v1 import sw_update_manager
from dcmanagerclient import utils


class SwPrestageManagerMixin(object):
    """This Mixin provides the update manager used for sw prestage."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.sw_prestage_manager
        return dcmanager_client.sw_prestage_manager


class CreateSwPrestageStrategy(SwPrestageManagerMixin,
                               sw_update_manager.CreateSwUpdateStrategy):
    """Create a prestage strategy."""

    def add_force_argument(self, parser):
        parser.add_argument(
            '--force',
            required=False,
            action='store_true',
            help='Skip checking the subcloud for \
                  management affecting alarms. '
        )

    def get_parser(self, prog_name):
        parser = super(CreateSwPrestageStrategy,
                       self).get_parser(prog_name)
        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password, will be prompted if not provided.'
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for prestage"""
        # Note the "-" vs "_" when dealing with parsed_args

        if parsed_args.sysadmin_password is not None:
            # The binary base64 encoded string (eg. b'dGVzdA==') is not JSON
            # serializable in Python3.x, so it has to be decoded to a JSON
            # serializable string (eg. 'dGVzdA==').
            kwargs_dict['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            kwargs_dict["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")).decode("utf-8")

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        pass


class ShowSwPrestageStrategy(SwPrestageManagerMixin,
                             sw_update_manager.ShowSwUpdateStrategy):
    """Show the details of a prestage strategy."""
    pass


class DeleteSwPrestageStrategy(SwPrestageManagerMixin,
                               sw_update_manager.DeleteSwUpdateStrategy):
    """Delete a prestage strategy."""
    pass


class ApplySwPrestageStrategy(SwPrestageManagerMixin,
                              sw_update_manager.ApplySwUpdateStrategy):
    """Apply a prestage strategy."""
    pass


class AbortSwPrestageStrategy(SwPrestageManagerMixin,
                              sw_update_manager.AbortSwUpdateStrategy):
    """Abort a prestage strategy."""
    pass
