# Copyright (c) 2020-2023 Wind River Systems, Inc.
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

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions


def _format(subcloud_deploy=None):
    columns = (
        'deploy_playbook',
        'deploy_overrides',
        'deploy_chart',
        'prestage_images',
        'software_version'
    )
    temp = list()
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
        parser = super(SubcloudDeployUpload, self).get_parser(prog_name)

        parser.add_argument(
            '--deploy-playbook',
            required=False,
            help='An ansible playbook to be run after the subcloud '
                 'has been successfully bootstrapped. It will be run with the '
                 'subcloud as the target and authentication is '
                 'handled automatically. '
                 'Must be a local file path'
        )

        parser.add_argument(
            '--deploy-overrides',
            required=False,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
                 'Must be a local file path'
        )

        parser.add_argument(
            '--deploy-chart',
            required=False,
            help='Deployment Manager helm chart to be passed to the '
                 'deploy playbook.'
                 'Must be a local file path'
        )

        parser.add_argument(
            '--prestage-images',
            required=False,
            help='Container image list to be passed to '
                 'prestage_images playbook. '
                 'Must be a local file path'
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
        dcmanager_client = self.app.client_manager.subcloud_deploy_manager

        data = dict()
        files = dict()
        variable_dict = {'deploy_playbook': parsed_args.deploy_playbook,
                         'deploy_overrides': parsed_args.deploy_overrides,
                         'deploy_chart': parsed_args.deploy_chart,
                         'prestage_images': parsed_args.prestage_images}
        for key, val in variable_dict.items():
            if val is None:
                continue
            elif not os.path.isfile(val):
                error_msg = f"{key} file does not exist: {val}"
                raise exceptions.DCManagerClientException(error_msg)
            files[key] = val

        if parsed_args.release is not None:
            data['release'] = parsed_args.release

        try:
            return dcmanager_client.subcloud_deploy_manager.\
                subcloud_deploy_upload(files=files, data=data)
        except Exception as e:
            print(e)
            error_msg = "Unable to upload subcloud deploy files"
            raise exceptions.DCManagerClientException(error_msg)


class SubcloudDeployShow(base.DCManagerShowOne):
    """Show the uploaded deployment files."""

    def _get_format_function(self):
        return _format

    def get_parser(self, prog_name):
        parser = super(SubcloudDeployShow, self).get_parser(prog_name)

        parser.add_argument(
            '--release',
            required=False,
            help='software release used to install, bootstrap and/or deploy '
                 'the subcloud with. If not specified, the current software '
                 'release of the system controller will be used.'
        )
        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_deploy_manager
        return dcmanager_client.subcloud_deploy_manager.subcloud_deploy_show(
            parsed_args.release)


class DeprecatedSubcloudDeployShow(SubcloudDeployShow):
    def _get_resources(self, parsed_args):
        deprecation_msg = ('This command has been deprecated. Please use '
                           'subcloud deploy show instead.')
        raise exceptions.DCManagerClientException(deprecation_msg)


class DeprecatedSubcloudDeployUpload(SubcloudDeployUpload):
    def _get_resources(self, parsed_args):
        deprecation_msg = ('This command has been deprecated. Please use '
                           'subcloud deploy upload instead.')
        raise exceptions.DCManagerClientException(deprecation_msg)
