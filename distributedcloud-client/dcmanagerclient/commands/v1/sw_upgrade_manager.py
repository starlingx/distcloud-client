# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2020-2023 Wind River Systems, Inc.
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
from dcmanagerclient.commands.v1 import sw_update_manager


class SwUpgradeManagerMixin(object):
    """This Mixin provides the update manager used for software upgrades."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.sw_upgrade_manager
        return dcmanager_client.sw_upgrade_manager

    def custom_format_function(self, sw_update_strategy=None):
        original_fmt_func = super()._get_format_function()
        columns, data = original_fmt_func(sw_update_strategy)
        if sw_update_strategy and sw_update_strategy.extra_args:
            upload_only = sw_update_strategy.extra_args.get("upload-only",
                                                            False)
        else:
            upload_only = False
        # Insert the 'upload only' field before the 'state',
        # 'created_at' and 'updated_at' fields
        columns = columns[:-3] + ("upload only",) + columns[-3:]
        data = data[:-3] + (upload_only,) + data[-3:]
        return columns, data

    def _get_format_function(self):
        return self.custom_format_function


class CreateSwUpgradeStrategy(SwUpgradeManagerMixin,
                              sw_update_manager.CreateSwUpdateStrategy):
    """Create a software upgrade strategy."""
    def add_force_argument(self, parser):
        parser.add_argument(
            '--force',
            required=False,
            action='store_true',
            help='Allow upgrade with the subcloud group \
                  rather than a single subcloud name/ID'
        )

    def get_parser(self, prog_name):
        parser = super(CreateSwUpgradeStrategy,
                       self).get_parser(prog_name)

        parser.add_argument(
            '--upload-only',
            required=False,
            action='store_true',
            help='Stops strategy after uploading releases to subclouds'
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for patching"""
        if parsed_args.upload_only:
            kwargs_dict['upload-only'] = 'true'
        else:
            kwargs_dict['upload-only'] = 'false'

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        pass


class ShowSwUpgradeStrategy(SwUpgradeManagerMixin,
                            sw_update_manager.ShowSwUpdateStrategy):
    """Show the details of a software upgrade strategy for a subcloud."""
    pass


class DeleteSwUpgradeStrategy(SwUpgradeManagerMixin,
                              sw_update_manager.DeleteSwUpdateStrategy):
    """Delete software upgrade strategy from the database."""
    pass


class ApplySwUpgradeStrategy(SwUpgradeManagerMixin,
                             sw_update_manager.ApplySwUpdateStrategy):
    """Apply a software upgrade strategy."""
    pass


class AbortSwUpgradeStrategy(SwUpgradeManagerMixin,
                             sw_update_manager.AbortSwUpdateStrategy):
    """Abort a software upgrade strategy."""
    pass
