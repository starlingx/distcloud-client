# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2024 Wind River Systems, Inc.
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


class SwPatchManagerMixin(object):
    """This Mixin provides the update manager used for sw patch."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.sw_patch_manager
        return dcmanager_client.sw_patch_manager

    def custom_format_function(self, sw_update_strategy=None):
        original_fmt_func = super()._get_format_function()
        columns, data = original_fmt_func(sw_update_strategy)

        if sw_update_strategy.extra_args:
            upload_only = sw_update_strategy.extra_args.get("upload-only", False)
        else:
            upload_only = False

        # Insert the 'upload only' field before the 'state',
        # 'created_at' and 'updated_at' fields
        columns = columns[:-3] + ("upload only",) + columns[-3:]
        data = data[:-3] + (upload_only,) + data[-3:]

        return columns, data

    def _get_format_function(self):
        return self.custom_format_function


class CreatePatchUpdateStrategy(
    SwPatchManagerMixin, sw_update_manager.CreateSwUpdateStrategy
):
    """Create a patch update strategy."""

    def get_parser(self, prog_name):
        parser = super(CreatePatchUpdateStrategy, self).get_parser(prog_name)

        parser.add_argument(
            "--upload-only",
            required=False,
            action="store_true",
            help="Stops strategy after uploading patches to subclouds",
        )
        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for patching"""
        if parsed_args.upload_only:
            kwargs_dict["upload-only"] = "true"
        else:
            kwargs_dict["upload-only"] = "false"


class ShowPatchUpdateStrategy(
    SwPatchManagerMixin, sw_update_manager.ShowSwUpdateStrategy
):
    """Show the details of a patch update strategy for a subcloud."""


class DeletePatchUpdateStrategy(
    SwPatchManagerMixin, sw_update_manager.DeleteSwUpdateStrategy
):
    """Delete patch update strategy from the database."""


class ApplyPatchUpdateStrategy(
    SwPatchManagerMixin, sw_update_manager.ApplySwUpdateStrategy
):
    """Apply a patch update strategy."""


class AbortPatchUpdateStrategy(
    SwPatchManagerMixin, sw_update_manager.AbortSwUpdateStrategy
):
    """Abort a patch update strategy."""
