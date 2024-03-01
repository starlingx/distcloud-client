# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2020-2024 Wind River Systems, Inc.
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


class SwUpgradeManagerMixin:
    """This Mixin provides the update manager used for software upgrades."""

    def get_sw_update_manager(self):
        sw_upgrade_manager = self.app.client_manager.sw_upgrade_manager
        return sw_upgrade_manager


class CreateSwUpgradeStrategy(
    SwUpgradeManagerMixin, sw_update_manager.CreateSwUpdateStrategy
):
    """Create a software upgrade strategy."""

    def add_force_argument(self, parser):
        parser.add_argument(
            "--force",
            required=False,
            action="store_true",
            help=(
                "Allow upgrade with the subcloud group "
                "rather than a single subcloud name/ID"
            ),
        )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        return parser

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        pass


class ShowSwUpgradeStrategy(
    SwUpgradeManagerMixin, sw_update_manager.ShowSwUpdateStrategy
):
    """Show the details of a software upgrade strategy for a subcloud."""


class DeleteSwUpgradeStrategy(
    SwUpgradeManagerMixin, sw_update_manager.DeleteSwUpdateStrategy
):
    """Delete software upgrade strategy from the database."""


class ApplySwUpgradeStrategy(
    SwUpgradeManagerMixin, sw_update_manager.ApplySwUpdateStrategy
):
    """Apply a software upgrade strategy."""


class AbortSwUpgradeStrategy(
    SwUpgradeManagerMixin, sw_update_manager.AbortSwUpdateStrategy
):
    """Abort a software upgrade strategy."""
