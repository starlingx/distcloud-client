# Copyright (c) 2020-2025 Wind River Systems, Inc.
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


import os

from osc_lib.command import command

from dcmanagerclient import exceptions
from dcmanagerclient.commands.v1 import base
from dcmanagerclient.commands.v1.base import ConfirmationMixin


def _format(subcloud_deploy=None):
    columns = (
        "deploy_playbook",
        "deploy_overrides",
        "deploy_chart",
        "prestage_images",
        "software_version",
    )
    temp = []
    try:
        temp.append(subcloud_deploy.deploy_playbook)
    except Exception:
        temp.append(None)
    try:
        temp.append(subcloud_deploy.deploy_overrides)
    except Exception:
        temp.append(None)
    try:
        temp.append(subcloud_deploy.deploy_chart)
    except Exception:
        temp.append(None)
    try:
        temp.append(subcloud_deploy.prestage_images)
    except Exception:
        temp.append(None)
    try:
        temp.append(subcloud_deploy.software_version)
    except Exception:
        temp.append(None)

    data = tuple(temp)

    return columns, data


class SubcloudDeployUpload(base.DCManagerShowOne):
    """Upload the subcloud deployment files"""

    def _get_format_function(self):
        return _format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--deploy-playbook",
            required=False,
            help=(
                "An ansible playbook to be run after the subcloud has been "
                "successfully bootstrapped. It will be run with the subcloud as the "
                "target and authentication is handled automatically. Must be a local "
                "file path."
            ),
        )

        parser.add_argument(
            "--deploy-overrides",
            required=False,
            help="YAML file containing subcloud variables to be passed to the "
            "deploy playbook. Must be a local file path",
        )

        parser.add_argument(
            "--deploy-chart",
            required=False,
            help="Deployment Manager helm chart to be passed to the "
            "deploy playbook. Must be a local file path",
        )

        parser.add_argument(
            "--prestage-images",
            required=False,
            help="Container image list to be passed to prestage_images playbook. "
            "Must be a local file path",
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
        subcloud_deploy_manager = self.app.client_manager.subcloud_deploy_manager

        data = {}
        files = {}
        variable_dict = {
            "deploy_playbook": parsed_args.deploy_playbook,
            "deploy_overrides": parsed_args.deploy_overrides,
            "deploy_chart": parsed_args.deploy_chart,
            "prestage_images": parsed_args.prestage_images,
        }
        for key, val in variable_dict.items():
            if val is None:
                continue
            if not os.path.isfile(val):
                error_msg = f"{key} file does not exist: {val}"
                raise exceptions.DCManagerClientException(error_msg)
            files[key] = val

        if parsed_args.release is not None:
            data["release"] = parsed_args.release

        try:
            return subcloud_deploy_manager.subcloud_deploy_upload(
                files=files, data=data
            )
        except Exception as exc:
            print(exc)
            error_msg = "Unable to upload subcloud deploy files"
            raise exceptions.DCManagerClientException(error_msg)


class SubcloudDeployShow(base.DCManagerShowOne):
    """Show the uploaded deployment files."""

    def _get_format_function(self):
        return _format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--release",
            required=False,
            help="software release used to install, bootstrap and/or deploy "
            "the subcloud with. If not specified, the current software "
            "release of the system controller will be used.",
        )
        return parser

    def _get_resources(self, parsed_args):
        subcloud_deploy_manager = self.app.client_manager.subcloud_deploy_manager
        return subcloud_deploy_manager.subcloud_deploy_show(parsed_args.release)


class DeprecatedSubcloudDeployShow(SubcloudDeployShow):
    DEPRECATION_MESSAGE = (
        "This command has been deprecated. Please use subcloud deploy show instead."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument_group(title="Notice", description=self.DEPRECATION_MESSAGE)
        return parser

    def _get_resources(self, _):
        raise exceptions.DCManagerClientException(self.DEPRECATION_MESSAGE)


class DeprecatedSubcloudDeployUpload(SubcloudDeployUpload):
    DEPRECATION_MESSAGE = (
        "This command has been deprecated. Please use subcloud deploy upload instead."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument_group(title="Notice", description=self.DEPRECATION_MESSAGE)
        return parser

    def _get_resources(self, _):
        raise exceptions.DCManagerClientException(self.DEPRECATION_MESSAGE)


class SubcloudDeployDelete(ConfirmationMixin, command.Command):
    """Delete the uploaded subcloud deployment files"""

    requires_confirmation = True

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--release",
            required=False,
            help="Release version that the user is trying to delete "
            "If not specified, the current software "
            "release of the system controller will be used.",
        )

        parser.add_argument(
            "--prestage-images",
            required=False,
            action="store_true",
            help="Delete prestage images list file only ",
        )

        parser.add_argument(
            "--deployment-files",
            required=False,
            action="store_true",
            help="Delete deploy playbook, deploy overrides, deploy chart files ",
        )
        return parser

    def take_action(self, parsed_args):
        super().take_action(parsed_args)
        subcloud_deploy_manager = self.app.client_manager.subcloud_deploy_manager
        release = parsed_args.release
        data = {}
        if parsed_args.prestage_images is not None:
            data["prestage_images"] = str(parsed_args.prestage_images)
        if parsed_args.deployment_files is not None:
            data["deployment_files"] = str(parsed_args.deployment_files)

        try:
            subcloud_deploy_manager.subcloud_deploy_delete(release, data=data)
        except Exception as exc:
            print(exc)
            error_msg = "Unable to delete subcloud deploy files"
            raise exceptions.DCManagerClientException(error_msg)
