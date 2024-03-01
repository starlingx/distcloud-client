# Copyright (c) 2022-2024 Wind River Systems, Inc.
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

from dcmanagerclient import exceptions
from dcmanagerclient import utils
from dcmanagerclient.commands.v1 import sw_update_manager


class SwPrestageManagerMixin:
    """This Mixin provides the update manager used for sw prestage."""

    def get_sw_update_manager(self):
        sw_prestage_manager = self.app.client_manager.sw_prestage_manager
        return sw_prestage_manager

    def custom_format_function(self, sw_update_strategy=None):
        original_fmt_func = super()._get_format_function()
        columns, data = original_fmt_func(sw_update_strategy)

        if sw_update_strategy.extra_args:
            prestage_software_version = sw_update_strategy.extra_args.get(
                "prestage-software-version"
            )
            if prestage_software_version:
                # Insert the 'software version' field before the 'state',
                # 'created_at' and 'updated_at' fields if it's present
                columns = columns[:-3] + ("prestage software version",) + columns[-3:]
                data = data[:-3] + (prestage_software_version,) + data[-3:]

        return columns, data

    def _get_format_function(self):
        return self.custom_format_function


class CreateSwPrestageStrategy(
    SwPrestageManagerMixin, sw_update_manager.CreateSwUpdateStrategy
):
    """Create a prestage strategy."""

    def add_force_argument(self, parser):
        parser.add_argument(
            "--force",
            required=False,
            action="store_true",
            help="Skip checking the subcloud for management affecting alarms.",
        )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password, will be prompted if not provided.",
        )
        parser.add_argument(
            "--release",
            required=False,
            help=(
                "software release used to prestage the subcloud with. "
                "Format: YY.MM or YY.MM.nn. "
                "If not specified, the current software release of "
                "the subcloud will be used."
            ),
        )
        parser.add_argument(
            "--for-install",
            required=False,
            action="store_true",
            help=("Prestage for installation. This is the default prestaging option."),
        )
        # Prestaging for deployment means prestaging for upgrade
        # For this operation, there is NO INSTALL phase anymore with USM
        # - targets the live ostree repo on the subcloud (not /opt/platform-backup)
        parser.add_argument(
            "--for-sw-deploy",
            required=False,
            action="store_true",
            help=(
                "Prestage for software deploy operations. If not specified, "
                "prestaging is targeted towards full installation."
            ),
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for prestage"""
        # Note the "-" vs "_" when dealing with parsed_args

        if parsed_args.sysadmin_password is not None:
            # The binary base64 encoded string (eg. b'dGVzdA==') is not JSON
            # serializable in Python3.x, so it has to be decoded to a JSON
            # serializable string (eg. 'dGVzdA==').
            kwargs_dict["sysadmin_password"] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")
            ).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            kwargs_dict["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")
            ).decode("utf-8")

        if parsed_args.release is not None:
            kwargs_dict["release"] = parsed_args.release

        if parsed_args.for_sw_deploy:
            if parsed_args.for_install:
                error_msg = (
                    "Options --for-install and --for-sw-deploy cannot be combined"
                )
                raise exceptions.DCManagerClientException(error_msg)
            kwargs_dict["for_sw_deploy"] = "true"
        else:
            # for_install is the default
            kwargs_dict["for_install"] = "true"

    # override validate_force_params defined in CreateSwUpdateStrategy
    def validate_force_params(self, parsed_args):
        pass


class ShowSwPrestageStrategy(
    SwPrestageManagerMixin, sw_update_manager.ShowSwUpdateStrategy
):
    """Show the details of a prestage strategy."""


class DeleteSwPrestageStrategy(
    SwPrestageManagerMixin, sw_update_manager.DeleteSwUpdateStrategy
):
    """Delete a prestage strategy."""


class ApplySwPrestageStrategy(
    SwPrestageManagerMixin, sw_update_manager.ApplySwUpdateStrategy
):
    """Apply a prestage strategy."""


class AbortSwPrestageStrategy(
    SwPrestageManagerMixin, sw_update_manager.AbortSwUpdateStrategy
):
    """Abort a prestage strategy."""
