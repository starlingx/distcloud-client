# Copyright (c) 2017 Ericsson AB.
# Copyright (c) 2017-2025 Wind River Systems, Inc.
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
import os

from osc_lib.command import command

from dcmanagerclient import exceptions
from dcmanagerclient import utils
from dcmanagerclient.commands.v1 import base
from dcmanagerclient.commands.v1.base import ConfirmationMixin

SET_FIELD_VALUE_DICT = {"region_name": None, "info_message": None}


def basic_format(subcloud=None):
    columns = (
        "id",
        "name",
        "management",
        "availability",
        "deploy status",
        "sync",
        "backup status",
        "prestage status",
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.management_state,
            subcloud.availability_status,
            subcloud.deploy_status,
            subcloud.sync_status,
            subcloud.backup_status,
            subcloud.prestage_status,
        )

    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def basic_detail_format(subcloud=None):
    columns = (
        "id",
        "name",
        "description",
        "location",
        "software_version",
        "management",
        "availability",
        "deploy_status",
        "management_subnet",
        "management_start_ip",
        "management_end_ip",
        "management_gateway_ip",
        "systemcontroller_gateway_ip",
        "group_id",
        "peer_group_id",
        "created_at",
        "updated_at",
        "backup_status",
        "backup_datetime",
        "prestage_status",
        "prestage_versions",
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.description,
            subcloud.location,
            subcloud.software_version,
            subcloud.management_state,
            subcloud.availability_status,
            subcloud.deploy_status,
            subcloud.management_subnet,
            subcloud.management_start_ip,
            subcloud.management_end_ip,
            subcloud.management_gateway_ip,
            subcloud.systemcontroller_gateway_ip,
            subcloud.group_id,
            subcloud.peer_group_id,
            subcloud.created_at,
            subcloud.updated_at,
            subcloud.backup_status,
            subcloud.backup_datetime,
            subcloud.prestage_status,
            subcloud.prestage_versions,
        )
    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


def detail_format(subcloud=None):
    columns, data = basic_detail_format(subcloud)
    if subcloud:
        for _listitem, sync_status in enumerate(subcloud.endpoint_sync_status):
            added_field = (sync_status["endpoint_type"] + "_sync_status",)
            added_value = (sync_status["sync_status"],)
            columns += tuple(added_field)
            data += tuple(added_value)

        if subcloud.oam_floating_ip != "unavailable":
            columns += ("oam_floating_ip",)
            data += (subcloud.oam_floating_ip,)

        if subcloud.deploy_config_sync_status != "unknown":
            columns += ("deploy_config_sync_status",)
            data += (subcloud.deploy_config_sync_status,)

    return columns, data


def detail_prestage_format(subcloud=None):
    columns, data = detail_format(subcloud)

    if subcloud and subcloud.prestage_software_version:
        columns += ("prestage_software_version",)
        data += (subcloud.prestage_software_version,)

    return columns, data


def detail_show_format(subcloud=None):
    columns, data = detail_format(subcloud)
    if subcloud and subcloud.region_name:
        columns += ("region_name",)
        data += (subcloud.region_name,)
    return columns, data


def detail_list_format(subcloud=None):
    columns, data = basic_detail_format(subcloud)

    # Find the index of 'deploy_status' in the tuple
    deploy_status_index = columns.index("deploy_status")

    # Insert "sync" field after 'deploy_status'
    columns = (
        columns[: deploy_status_index + 1]
        + ("sync",)
        + columns[deploy_status_index + 1 :]
    )

    if subcloud:
        data = (
            data[: deploy_status_index + 1]
            + (subcloud.sync_status,)
            + data[deploy_status_index + 1 :]
        )
    else:
        data = (tuple("<none>" for _ in range(len(columns))),)

    return columns, data


# The API is returning the region_name field, however only the list
# and show commands should consider the region name field.
# The other commands do not required it, since the output should
# not show that field
def update_fields_values(result):
    if len(result) == 0:
        return

    for item in result:
        for field, value in SET_FIELD_VALUE_DICT.items():
            if field in dir(item):
                setattr(item, field, value)


class AddSubcloud(base.DCManagerShowOne):
    """Add a new subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument("--name", required=False, help="Subcloud name")

        self.add_argument(
            "--bootstrap-address",
            required=True,
            help="IP address for initial subcloud controller.",
        )

        self.add_argument(
            "--bootstrap-values",
            required=True,
            help="YAML file containing parameters required for the bootstrap "
            "of the subcloud.",
        )

        self.add_argument(
            "--deploy-config",
            required=False,
            help="YAML file containing parameters required for the initial "
            "configuration and unlock of the subcloud.",
        )

        self.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the "
            "remote install of the subcloud.",
        )

        self.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        self.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, "
            "if not provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )

        self.add_argument(
            "--group", required=False, help="Name or ID of subcloud group."
        )

        self.add_argument(
            "--migrate",
            required=False,
            action="store_true",
            help="Migrate a subcloud from another distributed cloud.",
        )

        self.add_argument(
            "--release",
            required=False,
            help="software release used to install, bootstrap and/or deploy "
            "the subcloud with. If not specified, the current software "
            "release of the system controller will be used.",
        )

        self.add_argument(
            "--enroll", required=False, action="store_true", help="Enroll a subcloud"
        )

        self.add_argument(
            "--cloud-init-config",
            required=False,
            help="Path to a tarball file containing cloud-init scripts to be "
            "used during the enrollment process.",
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_manager = self.app.client_manager.subcloud_manager
        files = {}
        data = {}
        data["bootstrap-address"] = parsed_args.bootstrap_address

        # Get the install values yaml file
        if parsed_args.install_values is not None:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = (
                    f"install-values does not exist: {parsed_args.install_values}"
                )

                raise exceptions.DCManagerClientException(error_msg)
            files["install_values"] = parsed_args.install_values

        # Get the bootstrap values yaml file
        if not os.path.isfile(parsed_args.bootstrap_values):
            error_msg = (
                f"bootstrap-values does not exist: {parsed_args.bootstrap_values}"
            )
            raise exceptions.DCManagerClientException(error_msg)
        files["bootstrap_values"] = parsed_args.bootstrap_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config is not None:
            if parsed_args.migrate:
                error_msg = "migrate with deploy-config is not allowed"
                raise exceptions.DCManagerClientException(error_msg)

            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = f"deploy-config does not exist: {parsed_args.deploy_config}"
                raise exceptions.DCManagerClientException(error_msg)
            files["deploy_config"] = parsed_args.deploy_config

        if parsed_args.migrate and parsed_args.enroll:
            error_msg = "cannot run --migrate and --enroll options together"
            raise exceptions.DCManagerClientException(error_msg)

        if not parsed_args.install_values and parsed_args.enroll:
            error_msg = "install-values is required for --enroll option"
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.cloud_init_config:
            if not parsed_args.enroll:
                error_msg = "cloud-init-config is only valid with --enroll option"
                raise exceptions.DCManagerClientException(error_msg)

            utils.validate_cloud_init_config(parsed_args.cloud_init_config)
            files["cloud_init_config"] = parsed_args.cloud_init_config

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.sysadmin_password is not None:
            data["sysadmin_password"] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")
            )
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(password.encode("utf-8"))

        if parsed_args.install_values is not None:
            if parsed_args.bmc_password is not None:
                data["bmc_password"] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password("bmc")
                data["bmc_password"] = base64.b64encode(password.encode("utf-8"))

        if parsed_args.group is not None:
            data["group_id"] = parsed_args.group

        if parsed_args.migrate:
            data["migrate"] = "true"

        if parsed_args.enroll:
            data["enroll"] = "true"

        if parsed_args.release is not None:
            data["release"] = parsed_args.release

        if parsed_args.name is not None:
            if parsed_args.migrate:
                data["name"] = parsed_args.name
            else:
                error_msg = "The --name option can only be used with \
                    --migrate option."
                raise exceptions.DCManagerClientException(error_msg)

        result = subcloud_manager.add_subcloud(files=files, data=data)
        update_fields_values(result)
        return result


class ListSubcloud(base.DCManagerLister):
    """List subclouds."""

    def __init__(self, app, app_args):
        super().__init__(app, app_args)
        # Set a flag to indicate displaying a basic column list or
        # a list with customized or all columns
        self.show_basic_list = True

    def _validate_parsed_args(self, parsed_args):
        self.show_basic_list = not (parsed_args.columns or parsed_args.detail)

    def _get_format_function(self):
        return basic_format if self.show_basic_list else detail_list_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        self.add_argument(
            "--all",
            required=False,
            action="store_true",
            help='List all subclouds include "secondary" state subclouds',
        )
        self.add_argument(
            "-d",
            "--detail",
            required=False,
            action="store_true",
            help="List all columns of the subclouds",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_manager = self.app.client_manager.subcloud_manager
        subclouds = subcloud_manager.list_subclouds()

        # for '--all' parameter, show all subclouds.
        # for no parameter, hidden all 'secondary/secondary-failed'
        # state subclouds.
        if parsed_args.all:
            return subclouds
        filtered_subclouds = [
            s
            for s in subclouds
            if s.deploy_status not in ("secondary", "secondary-failed")
        ]
        return filtered_subclouds


class ShowSubcloud(base.DCManagerShowOne):
    """Show the details of a subcloud."""

    def _get_format_function(self):
        return detail_show_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "subcloud", help="Name or ID of subcloud to view the details."
        )

        self.add_argument(
            "-d",
            "--detail",
            action="store_true",
            help="Show additional details for a subcloud",
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        if not subcloud_ref:
            raise exceptions.DCManagerClientException(
                "Subcloud cannot be an empty value."
            )
        subcloud_manager = self.app.client_manager.subcloud_manager

        if parsed_args.detail:
            return subcloud_manager.subcloud_additional_details(subcloud_ref)
        return subcloud_manager.subcloud_detail(subcloud_ref)


class ShowSubcloudError(base.DCManagerBase, command.Command):
    """Show the error of the last failed operation."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "subcloud", help="Name or ID of subcloud to view the errors details."
        )
        return parser

    def take_action(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        if not subcloud_ref:
            raise exceptions.DCManagerClientException(
                "Subcloud cannot be an empty value."
            )
        subcloud_manager = self.app.client_manager.subcloud_manager
        ret = subcloud_manager.subcloud_detail(subcloud_ref)
        data = ret[0].error_description
        print("".join(data))


class DeleteSubcloud(ConfirmationMixin, command.Command):
    """Delete subcloud details from the database."""

    requires_confirmation = True

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument("subcloud", help="Name or ID of the subcloud to delete.")
        return parser

    def take_action(self, parsed_args):
        super().take_action(parsed_args)
        subcloud_ref = parsed_args.subcloud
        subcloud_manager = self.app.client_manager.subcloud_manager
        try:
            subcloud_manager.delete_subcloud(subcloud_ref)
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to delete subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class UnmanageSubcloud(base.DCManagerShowOne):
    """Unmanage a subcloud."""

    requires_confirmation = True

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument("subcloud", help="Name or ID of the subcloud to unmanage.")

        self.add_argument(
            "--migrate",
            required=False,
            action="store_true",
            help="Mark the subcloud for an upcoming migration.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        subcloud_manager = self.app.client_manager.subcloud_manager
        kwargs = {}
        kwargs["management-state"] = "unmanaged"

        if parsed_args.migrate:
            kwargs["migrate"] = "true"

        try:
            result = subcloud_manager.update_subcloud(
                subcloud_ref, files=None, data=kwargs
            )
            update_fields_values(result)
            return result
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to unmanage subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class ManageSubcloud(base.DCManagerShowOne):
    """Manage a subcloud."""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument("subcloud", help="Name or ID of the subcloud to manage.")

        self.add_argument(
            "--force",
            required=False,
            action="store_true",
            help="Disregard subcloud availability status, intended for \
                  some upgrade recovery scenarios.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        subcloud_manager = self.app.client_manager.subcloud_manager
        kwargs = {}
        kwargs["management-state"] = "managed"
        if parsed_args.force:
            kwargs["force"] = "true"

        try:
            result = subcloud_manager.update_subcloud(
                subcloud_ref, files=None, data=kwargs
            )
            update_fields_values(result)
            return result
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to manage subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class UpdateSubcloud(base.DCManagerShowOne):
    """Update attributes of a subcloud."""

    requires_confirmation = True
    _info_message = None

    def produce_output(self, parsed_args, column_names, data):
        """Overrides method from cliff.Lister/cliff.ShowOne."""

        # Print out a note or informational message above the formatted
        # response.
        if self._info_message:
            self.app.stdout.write(self._info_message)

        return super().produce_output(parsed_args, column_names, data)

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument("subcloud", help="Name or ID of the subcloud to update.")

        self.add_argument("--name", required=False, help="Name of subcloud.")

        self.add_argument(
            "--description", required=False, help="Description of subcloud."
        )

        self.add_argument("--location", required=False, help="Location of subcloud.")

        self.add_argument(
            "--group", required=False, help="Name or ID of subcloud group."
        )

        self.add_argument(
            "--management-subnet", required=False, help="Network subnet of subcloud."
        )

        self.add_argument(
            "--management-gateway-ip",
            required=False,
            help="Network gateway IP of subcloud.",
        )

        self.add_argument(
            "--management-start-ip",
            required=False,
            help="Network start IP of subcloud.",
        )

        self.add_argument(
            "--management-end-ip", required=False, help="Network end IP of subcloud."
        )

        self.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be updated, "
            "if not provided you will be prompted.",
        )

        self.add_argument(
            "--bootstrap-address",
            required=False,
            help="bootstrap address of the subcloud to be updated.",
        )

        self.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the "
            "remote install of the subcloud.",
        )

        self.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, if not "
            "provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )
        self.add_argument(
            "--bootstrap-values",
            required=False,
            help="YAML file containing subcloud configuration settings. "
            "Can be either a local file path or a URL.",
        )
        self.add_argument(
            "--peer-group",
            required=False,
            help="Name or ID of subcloud peer group (for migrate).",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        subcloud_manager = self.app.client_manager.subcloud_manager
        files = {}
        data = {}

        if parsed_args.name:
            data["name"] = parsed_args.name
        if parsed_args.description:
            data["description"] = parsed_args.description
        if parsed_args.location:
            data["location"] = parsed_args.location
        if parsed_args.group:
            data["group_id"] = parsed_args.group
        if parsed_args.management_subnet:
            data["management_subnet"] = parsed_args.management_subnet
        if parsed_args.management_gateway_ip:
            data["management_gateway_ip"] = parsed_args.management_gateway_ip
        if parsed_args.management_start_ip:
            data["management_start_ip"] = parsed_args.management_start_ip
        if parsed_args.management_end_ip:
            data["management_end_ip"] = parsed_args.management_end_ip
        if parsed_args.bootstrap_address:
            data["bootstrap_address"] = parsed_args.bootstrap_address
        if parsed_args.peer_group:
            data["peer_group"] = parsed_args.peer_group

        subcloud_network_values = [
            data.get("management_subnet"),
            data.get("management_gateway_ip"),
            data.get("management_start_ip"),
            data.get("management_end_ip"),
            data.get("bootstrap_address"),
        ]

        # Semantic check if the required arguments for updating admin network
        if all(value is not None for value in subcloud_network_values):
            # Prompt the user for the subcloud's password if it isn't provided
            if parsed_args.sysadmin_password is not None:
                data["sysadmin_password"] = base64.b64encode(
                    parsed_args.sysadmin_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password()
                data["sysadmin_password"] = base64.b64encode(password.encode("utf-8"))
        # For subcloud network reconfiguration
        # If any management_* presents, need all
        # management_subnet/management_gateway_ip/
        # management_start_ip/management_end_ip/bootstrap_address
        # presents.
        elif any(
            value is not None and value != parsed_args.bootstrap_address
            for value in subcloud_network_values
        ):
            # Not all network values exist
            error_msg = (
                "For subcloud network reconfiguration request all the "
                "following parameters are necessary: --management-subnet, "
                "--management-gateway-ip, --management-start-ip, "
                "--management-end-ip and --bootstrap-address"
            )
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.install_values:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = (
                    f"install-values does not exist: {parsed_args.install_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["install_values"] = parsed_args.install_values

            if parsed_args.bmc_password is not None:
                data["bmc_password"] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password("bmc")
                data["bmc_password"] = base64.b64encode(password.encode("utf-8"))

        # Update the bootstrap values from yaml file
        if parsed_args.bootstrap_values:
            if not os.path.isfile(parsed_args.bootstrap_values):
                error_msg = (
                    f"bootstrap-values doesm't exist: {parsed_args.bootstrap_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["bootstrap_values"] = parsed_args.bootstrap_values

        if not (data or files):
            error_msg = "Nothing to update"
            raise exceptions.DCManagerClientException(error_msg)

        try:
            result = subcloud_manager.update_subcloud(
                subcloud_ref, files=files, data=data
            )
            self._info_message = getattr(result[0], "info_message")
            update_fields_values(result)
            return result
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to update subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class ReconfigSubcloud(base.DCManagerShowOne):
    """Reconfigure a subcloud."""

    requires_confirmation = True
    DEPRECATION_MESSAGE = (
        "This command has been deprecated. Please use 'subcloud deploy config' instead."
    )

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        self.add_argument_group(title="Notice", description=self.DEPRECATION_MESSAGE)
        return parser

    def _get_resources(self, parsed_args):
        raise exceptions.DCManagerClientException(self.DEPRECATION_MESSAGE)


class ReinstallSubcloud(base.DCManagerShowOne):
    """Reinstall a subcloud."""

    requires_confirmation = True
    DEPRECATION_MESSAGE = (
        "This command has been deprecated. Please use 'subcloud redeploy' instead."
    )

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        self.add_argument_group(title="Notice", description=self.DEPRECATION_MESSAGE)
        return parser

    def _get_resources(self, parsed_args):
        raise exceptions.DCManagerClientException(self.DEPRECATION_MESSAGE)


class RedeploySubcloud(base.DCManagerShowOne):
    """Redeploy a subcloud."""

    requires_confirmation = True

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument("subcloud", help="Name or ID of the subcloud to redeploy.")

        self.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the "
            "remote install of the subcloud.",
        )

        self.add_argument(
            "--bootstrap-values",
            required=False,
            help="YAML file containing subcloud configuration settings. "
            "Can be either a local file path or a URL.",
        )

        self.add_argument(
            "--deploy-config",
            required=False,
            help="YAML file containing subcloud variables to be passed to the "
            "deploy playbook.",
        )

        self.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        self.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, if not "
            "provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )

        self.add_argument(
            "--release",
            required=False,
            help="software release used to install, bootstrap and/or deploy "
            "the subcloud with. If not specified, the current software "
            "release of the system controller will be used.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        subcloud_manager = self.app.client_manager.subcloud_manager
        files = {}
        data = {}

        # Get the install values yaml file
        if parsed_args.install_values is not None:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = (
                    f"install-values does not exist: {parsed_args.install_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["install_values"] = parsed_args.install_values

        # Get the bootstrap values yaml file
        if parsed_args.bootstrap_values is not None:
            if not os.path.isfile(parsed_args.bootstrap_values):
                error_msg = (
                    "bootstrap-values does not exist: "
                    f"{parsed_args.bootstrap_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["bootstrap_values"] = parsed_args.bootstrap_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config is not None:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = f"deploy-config does not exist: {parsed_args.deploy_config}"
                raise exceptions.DCManagerClientException(error_msg)
            files["deploy_config"] = parsed_args.deploy_config

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.sysadmin_password is not None:
            data["sysadmin_password"] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")
            )
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(password.encode("utf-8"))

        if parsed_args.install_values:
            if parsed_args.bmc_password:
                data["bmc_password"] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password("bmc")
                data["bmc_password"] = base64.b64encode(password.encode("utf-8"))

        if parsed_args.release is not None:
            data["release"] = parsed_args.release

        try:
            return subcloud_manager.redeploy_subcloud(
                subcloud_ref=subcloud_ref, files=files, data=data
            )
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to redeploy subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class RestoreSubcloud(base.DCManagerShowOne):
    """Restore a subcloud."""

    DEPRECATION_MESSAGE = (
        "This command has been deprecated. Please use "
        "subcloud-backup restore instead."
    )

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        self.add_argument_group(title="Notice", description=self.DEPRECATION_MESSAGE)
        return parser

    def _get_resources(self, parsed_args):
        raise exceptions.DCManagerClientException(self.DEPRECATION_MESSAGE)


class PrestageSubcloud(base.DCManagerShowOne):
    """Prestage a subcloud."""

    def _get_format_function(self):
        return detail_prestage_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        self.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be prestaged, "
            "if not provided you will be prompted.",
        )

        self.add_argument("subcloud", help="Name or ID of the subcloud to prestage.")

        self.add_argument(
            "--force",
            required=False,
            action="store_true",
            help="Disregard subcloud management alarm condition",
        )

        self.add_argument(
            "--release",
            required=False,
            help="software release used to prestage the subcloud with. "
            "Format: YY.MM or YY.MM.nn. "
            "If not specified, the current software release of "
            "the subcloud will be used.",
        )

        self.add_argument(
            "--for-install",
            required=False,
            action="store_true",
            help=("Prestage for installation. This is the default prestaging option."),
        )
        # Prestaging for deployment means prestaging for upgrade
        # With USM there is no install phase for upgrades. This operation
        # therefore targets the live ostree repo on the subcloud (not
        # /opt/platform-backup)
        self.add_argument(
            "--for-sw-deploy",
            required=False,
            action="store_true",
            help=(
                "Prestage for software deploy operations. If not specified, "
                "prestaging is targeted towards full installation."
            ),
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        subcloud_manager = self.app.client_manager.subcloud_manager
        data = {}

        if parsed_args.force:
            data["force"] = "true"

        if parsed_args.sysadmin_password is not None:
            data["sysadmin_password"] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")
            ).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")
            ).decode("utf-8")

        if parsed_args.release:
            data["release"] = parsed_args.release
        if parsed_args.for_sw_deploy:
            if parsed_args.for_install:
                error_msg = (
                    "Options --for-install and --for-sw-deploy cannot be combined"
                )
                raise exceptions.DCManagerClientException(error_msg)
            data["for_sw_deploy"] = "true"
        else:
            # for_install is the default
            data["for_install"] = "true"

        try:
            result = subcloud_manager.prestage_subcloud(
                subcloud_ref=subcloud_ref, data=data
            )
            update_fields_values(result)
            return result

        except exceptions.DCManagerClientException:
            raise

        except Exception as exc:
            print(exc)
            error_msg = f"Unable to prestage subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)
