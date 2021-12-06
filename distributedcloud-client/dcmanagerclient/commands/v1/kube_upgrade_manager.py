# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2020-2021 Wind River Systems, Inc.
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


class KubeUpgradeManagerMixin(object):
    """This Mixin provides the update manager used for kubernetes upgrades."""

    def get_sw_update_manager(self):
        dcmanager_client = self.app.client_manager.kube_upgrade_manager
        return dcmanager_client.kube_upgrade_manager


class CreateKubeUpgradeStrategy(KubeUpgradeManagerMixin,
                                sw_update_manager.CreateSwUpdateStrategy):
    """Create a kubernetes upgrade strategy."""

    def get_parser(self, prog_name):
        parser = super(CreateKubeUpgradeStrategy,
                       self).get_parser(prog_name)
        parser.add_argument(
            '--to-version',
            required=False,
            help='Specify a version other than the system controller version.'
        )
        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for kube upgrade"""
        # Note the "-" vs "_" when dealing with parsed_args
        if parsed_args.to_version:
            kwargs_dict['to-version'] = parsed_args.to_version

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        """Disable validating the force option.  Allows multiple subclouds."""
        pass


class ShowKubeUpgradeStrategy(KubeUpgradeManagerMixin,
                              sw_update_manager.ShowSwUpdateStrategy):
    """Show the details of a kubernetes upgrade strategy for a subcloud."""
    pass


class DeleteKubeUpgradeStrategy(KubeUpgradeManagerMixin,
                                sw_update_manager.DeleteSwUpdateStrategy):
    """Delete kubernetes upgrade strategy from the database."""
    pass


class ApplyKubeUpgradeStrategy(KubeUpgradeManagerMixin,
                               sw_update_manager.ApplySwUpdateStrategy):
    """Apply a kubernetes upgrade strategy."""
    pass


class AbortKubeUpgradeStrategy(KubeUpgradeManagerMixin,
                               sw_update_manager.AbortSwUpdateStrategy):
    """Abort a kubernetes upgrade strategy."""
    pass
