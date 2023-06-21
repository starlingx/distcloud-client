#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64
import os

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions
from dcmanagerclient import utils


class CreatePhasedSubcloudDeploy(base.DCManagerShowOne):
    """Creates a new subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--bootstrap-address',
            required=True,
            help='IP address for initial subcloud controller.'
        )

        parser.add_argument(
            '--bootstrap-values',
            required=True,
            help='YAML file containing subcloud configuration settings. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--deploy-config',
            required=False,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
        )

        parser.add_argument(
            '--install-values',
            required=False,
            help='YAML file containing subcloud variables required for remote '
                 'install playbook.'
        )

        parser.add_argument(
            '--bmc-password',
            required=False,
            help='bmc password of the subcloud to be configured, '
                 'if not provided you will be prompted. This parameter is only'
                 ' valid if the --install-values are specified.'
        )

        parser.add_argument(
            '--group',
            required=False,
            help='Name or ID of subcloud group.'
        )

        parser.add_argument(
            '--release',
            required=False,
            help='software release used to install, bootstrap and/or deploy '
                 'the subcloud with. If not specified, the current software '
                 'release of the system controller will be used.'
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.\
            phased_subcloud_deploy_manager.phased_subcloud_deploy_manager
        files = dict()
        data = dict()

        data['bootstrap-address'] = parsed_args.bootstrap_address

        # Get the bootstrap values yaml file
        if not os.path.isfile(parsed_args.bootstrap_values):
            error_msg = "bootstrap-values does not exist: %s" % \
                        parsed_args.bootstrap_values
            raise exceptions.DCManagerClientException(error_msg)
        files['bootstrap_values'] = parsed_args.bootstrap_values

        # Get the deploy config yaml file
        if parsed_args.deploy_config:
            if not os.path.isfile(parsed_args.deploy_config):
                error_msg = "deploy-config does not exist: %s" % \
                            parsed_args.deploy_config
                raise exceptions.DCManagerClientException(error_msg)
            files['deploy_config'] = parsed_args.deploy_config

        # Get the install values yaml file
        if parsed_args.install_values:
            if not os.path.isfile(parsed_args.install_values):
                error_msg = "install-values does not exist: %s" % \
                            parsed_args.install_values
                raise exceptions.DCManagerClientException(error_msg)
            files['install_values'] = parsed_args.install_values

            if parsed_args.bmc_password:
                data['bmc_password'] = base64.b64encode(
                    parsed_args.bmc_password.encode("utf-8"))
            else:
                password = utils.prompt_for_password('bmc')
                data["bmc_password"] = base64.b64encode(
                    password.encode("utf-8"))

        if parsed_args.group:
            data['group_id'] = parsed_args.group

        if parsed_args.release:
            data['release'] = parsed_args.release

        return dcmanager_client.subcloud_deploy_create(
            files=files, data=data)


class BootstrapPhasedSubcloudDeploy(base.DCManagerShowOne):
    """Bootstrap a subcloud."""

    def _get_format_function(self):
        return utils.subcloud_detail_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'subcloud',
            help='Name or ID of the subcloud to bootstrap.'
        )

        parser.add_argument(
            '--bootstrap-address',
            required=False,
            help='IP address for initial subcloud controller.'
        )

        parser.add_argument(
            '--bootstrap-values',
            required=False,
            help='YAML file containing subcloud configuration settings. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be configured, '
                 'if not provided you will be prompted.'
        )

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.\
            phased_subcloud_deploy_manager.phased_subcloud_deploy_manager
        files = dict()
        data = dict()

        if parsed_args.bootstrap_address:
            data['bootstrap-address'] = parsed_args.bootstrap_address

        # Get the bootstrap values yaml file
        if parsed_args.bootstrap_values:
            if not os.path.isfile(parsed_args.bootstrap_values):
                error_msg = "bootstrap-values does not exist: %s" % \
                            parsed_args.bootstrap_values
                raise exceptions.DCManagerClientException(error_msg)
            files['bootstrap_values'] = parsed_args.bootstrap_values

        # Prompt the user for the subcloud's password if it isn't provided
        if parsed_args.sysadmin_password:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8"))
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8"))

        subcloud_ref = parsed_args.subcloud

        return dcmanager_client.subcloud_deploy_bootstrap(
            subcloud_ref, files=files, data=data)
