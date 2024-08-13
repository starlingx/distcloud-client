#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64
import os

from dcmanagerclient import exceptions, utils
from dcmanagerclient.commands.v1 import base


class AbortPhasedSubcloudDeploy(base.DCManagerShowOne):
    """Abort the subcloud deploy phase."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "subcloud",
            help="Name or ID of the subcloud to abort the on-going deployment.",
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )

        try:
            return phased_subcloud_deploy_manager.subcloud_deploy_abort(
                subcloud_ref=subcloud_ref
            )
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to abort subcloud deploy {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class PhasedSubcloudDeployResume(base.DCManagerShowOne):
    """Resume the subcloud deployment."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "subcloud", help="Name or ID of the subcloud to resume deployment."
        )

        parser.add_argument(
            "--bootstrap-address",
            required=False,
            help="IP address for initial subcloud controller.",
        )

        parser.add_argument(
            "--bootstrap-values",
            required=False,
            help="YAML file containing parameters required for the bootstrap "
            "of the subcloud.",
        )

        parser.add_argument(
            "--deploy-config",
            required=False,
            help="YAML file containing parameters required for the initial "
            "configuration and unlock of the subcloud.",
        )

        parser.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the remote "
            "install of the subcloud.",
        )

        parser.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        parser.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, "
            "if not provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )

        parser.add_argument(
            "--release",
            required=False,
            help="software release used to install, bootstrap and/or deploy "
            "the subcloud with. If not specified, the current software "
            "release of the system controller will be used.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )
        files = {}
        data = {}

        if parsed_args.bootstrap_address:
            data["bootstrap-address"] = parsed_args.bootstrap_address

        # Get the bootstrap values yaml file
        if parsed_args.bootstrap_values:
            if not os.path.isfile(parsed_args.bootstrap_values):
                error_msg = (
                    "bootstrap-values does not exist: "
                    f"{parsed_args.bootstrap_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["bootstrap_values"] = parsed_args.bootstrap_values

        # Get the install values yaml file
        if parsed_args.install_values:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = (
                    f"install-values does not exist: {parsed_args.install_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["install_values"] = parsed_args.install_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = f"deploy-config does not exist: {parsed_args.deploy_config}"
                raise exceptions.DCManagerClientException(error_msg)
            files["deploy_config"] = parsed_args.deploy_config

        # Prompt the user for the subcloud's password if it isn't provided
        utils.set_sysadmin_password(parsed_args, data)

        if parsed_args.install_values:
            if parsed_args.bmc_password:
                data["bmc_password"] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password("bmc")
                data["bmc_password"] = base64.b64encode(password.encode("utf-8"))

        if parsed_args.release:
            data["release"] = parsed_args.release

        return phased_subcloud_deploy_manager.subcloud_deploy_resume(
            subcloud_ref=subcloud_ref, files=files, data=data
        )


class CreatePhasedSubcloudDeploy(base.DCManagerShowOne):
    """Creates a new subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--bootstrap-address",
            required=True,
            help="IP address for initial subcloud controller.",
        )

        parser.add_argument(
            "--bootstrap-values",
            required=True,
            help="YAML file containing parameters required for the bootstrap "
            "of the subcloud.",
        )

        parser.add_argument(
            "--deploy-config",
            required=False,
            help="YAML file containing parameters required for the initial "
            "configuration and unlock of the subcloud.",
        )

        parser.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the remote "
            "install of the subcloud.",
        )

        parser.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, "
            "if not provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )

        parser.add_argument(
            "--group", required=False, help="Name or ID of subcloud group."
        )

        parser.add_argument(
            "--release",
            required=False,
            help="software release used to install, bootstrap and/or deploy "
            "the subcloud with. If not specified, the current software "
            "release of the system controller will be used.",
        )
        return parser

    def _get_resources(self, parsed_args):
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )
        files = {}
        data = {}

        data["bootstrap-address"] = parsed_args.bootstrap_address

        # Get the bootstrap values yaml file
        if not os.path.isfile(parsed_args.bootstrap_values):
            error_msg = (
                f"bootstrap-values does not exist: {parsed_args.bootstrap_values}"
            )
            raise exceptions.DCManagerClientException(error_msg)
        files["bootstrap_values"] = parsed_args.bootstrap_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = f"deploy-config does not exist: {parsed_args.deploy_config}"
                raise exceptions.DCManagerClientException(error_msg)
            files["deploy_config"] = parsed_args.deploy_config

        # Get the install values yaml file
        if parsed_args.install_values:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = (
                    f"install-values does not exist: {parsed_args.install_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["install_values"] = parsed_args.install_values

            if parsed_args.bmc_password:
                data["bmc_password"] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password("bmc")
                data["bmc_password"] = base64.b64encode(password.encode("utf-8"))

        if parsed_args.group:
            data["group_id"] = parsed_args.group

        if parsed_args.release:
            data["release"] = parsed_args.release

        return phased_subcloud_deploy_manager.subcloud_deploy_create(
            files=files, data=data
        )


class InstallPhasedSubcloudDeploy(base.DCManagerShowOne):
    """Install a subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("subcloud", help="Name or ID of the subcloud to install.")

        parser.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the remote "
            "install of the subcloud.",
        )

        parser.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        parser.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, "
            "if not provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )

        parser.add_argument(
            "--release",
            required=False,
            help="software release used to install the subcloud with. "
            "If not specified, the current software release "
            "of the system controller will be used.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )
        files = {}
        data = {}

        # Prompt the user for the subcloud's password if it isn't provided
        utils.set_sysadmin_password(parsed_args, data)

        if parsed_args.install_values is not None:
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

        if parsed_args.release is not None:
            data["release"] = parsed_args.release

        try:
            return phased_subcloud_deploy_manager.subcloud_deploy_install(
                subcloud_ref=subcloud_ref, files=files, data=data
            )
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to install subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class BootstrapPhasedSubcloudDeploy(base.DCManagerShowOne):
    """Bootstrap a subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("subcloud", help="Name or ID of the subcloud to bootstrap.")

        parser.add_argument(
            "--bootstrap-address",
            required=False,
            help="IP address for initial subcloud controller.",
        )

        parser.add_argument(
            "--bootstrap-values",
            required=False,
            help="YAML file containing parameters required for the bootstrap "
            "of the subcloud.",
        )

        parser.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        return parser

    def _get_resources(self, parsed_args):
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )
        files = {}
        data = {}

        if parsed_args.bootstrap_address:
            data["bootstrap-address"] = parsed_args.bootstrap_address

        # Get the bootstrap values yaml file
        if parsed_args.bootstrap_values:
            if not os.path.isfile(parsed_args.bootstrap_values):
                error_msg = (
                    "bootstrap-values does not exist: "
                    f"{parsed_args.bootstrap_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["bootstrap_values"] = parsed_args.bootstrap_values

        # Prompt the user for the subcloud's password if it isn't provided
        utils.set_sysadmin_password(parsed_args, data)

        subcloud_ref = parsed_args.subcloud

        return phased_subcloud_deploy_manager.subcloud_deploy_bootstrap(
            subcloud_ref, files=files, data=data
        )


class ConfigPhasedSubcloudDeploy(base.DCManagerShowOne):
    """Configure a subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("subcloud", help="Name or ID of the subcloud to update.")

        parser.add_argument(
            "--deploy-config",
            required=False,
            help="YAML file containing parameters required for the initial "
            "configuration and unlock of the subcloud.",
        )

        parser.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )
        files = {}
        data = {}

        # Get the deploy config yaml file
        if parsed_args.deploy_config is not None:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = (
                    f"deploy-config file does not exist: {parsed_args.deploy_config}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["deploy_config"] = parsed_args.deploy_config

        # Prompt the user for the subcloud's password if it isn't provided
        utils.set_sysadmin_password(parsed_args, data)

        try:
            return phased_subcloud_deploy_manager.subcloud_deploy_config(
                subcloud_ref=subcloud_ref, files=files, data=data
            )
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to configure subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class CompletePhasedSubcloudDeploy(base.DCManagerShowOne):
    """Complete a subcloud deployment."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "subcloud", help="Name or ID of the subcloud to complete the deployment."
        )

        return parser

    def _get_resources(self, parsed_args):
        subcloud_ref = parsed_args.subcloud
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )

        try:
            return phased_subcloud_deploy_manager.subcloud_deploy_complete(subcloud_ref)
        except Exception as exc:
            print(exc)
            error_msg = f"Unable to complete the deployment of subcloud {subcloud_ref}"
            raise exceptions.DCManagerClientException(error_msg)


class EnrollPhasedSubcloudDeploy(base.DCManagerShowOne):
    """Enrolls a subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument("subcloud", help="Name or ID of the subcloud to enroll.")

        parser.add_argument(
            "--install-values",
            required=False,
            help="YAML file containing parameters required for the "
            "enrollment of the subcloud.",
        )

        parser.add_argument(
            "--bootstrap-address",
            required=False,
            help="IP address for initial subcloud controller.",
        )

        parser.add_argument(
            "--bootstrap-values",
            required=False,
            help="YAML file containing the parameters required for the "
            "subcloud enrollment.",
        )

        parser.add_argument(
            "--sysadmin-password",
            required=False,
            help="sysadmin password of the subcloud to be configured, "
            "if not provided you will be prompted.",
        )

        parser.add_argument(
            "--bmc-password",
            required=False,
            help="bmc password of the subcloud to be configured, "
            "if not provided you will be prompted. This parameter is only"
            " valid if the --install-values are specified.",
        )

        return parser

    def _get_resources(self, parsed_args):
        phased_subcloud_deploy_manager = (
            self.app.client_manager.phased_subcloud_deploy_manager
        )
        files = {}
        data = {}

        if parsed_args.bootstrap_address:
            data["bootstrap-address"] = parsed_args.bootstrap_address

        # Get the bootstrap values yaml file
        if parsed_args.bootstrap_values:
            if not os.path.isfile(parsed_args.bootstrap_values):
                error_msg = (
                    "bootstrap-values does not exist: "
                    f"{parsed_args.bootstrap_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["bootstrap_values"] = parsed_args.bootstrap_values

        if parsed_args.install_values:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = (
                    f"install-values does not exist: {parsed_args.install_values}"
                )
                raise exceptions.DCManagerClientException(error_msg)
            files["install_values"] = parsed_args.install_values

        if parsed_args.install_values:
            if parsed_args.bmc_password:
                data["bmc_password"] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8")
                )
            else:
                password = utils.prompt_for_password("bmc")
                data["bmc_password"] = base64.b64encode(password.encode("utf-8"))

        utils.set_sysadmin_password(parsed_args, data)

        subcloud_ref = parsed_args.subcloud

        return phased_subcloud_deploy_manager.subcloud_deploy_enroll(
            subcloud_ref, files=files, data=data
        )
