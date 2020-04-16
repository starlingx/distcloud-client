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
# Copyright (c) 2020 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#


import os

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions


def _format(subcloud_deploy=None):
    columns = (
        'deploy_playbook',
        'deploy_overrides',
        'deploy_chart'
    )

    if subcloud_deploy:
        data = (
            subcloud_deploy.deploy_playbook,
            subcloud_deploy.deploy_overrides,
            subcloud_deploy.deploy_chart
        )

    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class SubcloudDeployUpload(base.DCManagerShowOne):
    """Upload the subcloud deployment files"""

    def _get_format_function(self):
        return _format

    def get_parser(self, prog_name):
        parser = super(SubcloudDeployUpload, self).get_parser(prog_name)

        parser.add_argument(
            '--deploy-playbook',
            required=True,
            help='An ansible playbook to be run after the subcloud '
                 'has been successfully bootstrapped. It will be run with the '
                 'subcloud as the target and authentication is '
                 'handled automatically. '
                 'Must be a local file path'
        )

        parser.add_argument(
            '--deploy-overrides',
            required=True,
            help='YAML file containing subcloud variables to be passed to the '
                 'deploy playbook.'
                 'Must be a local file path'
        )

        parser.add_argument(
            '--deploy-chart',
            required=True,
            help='Deployment Manager helm chart to be passed to the '
                 'deploy playbook.'
                 'Must be a local file path'
        )

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_deploy_manager
        kwargs = dict()
        if not os.path.isfile(parsed_args.deploy_playbook):
            error_msg = "deploy-playbook does not exist: %s" % \
                        parsed_args.deploy_playbook
            raise exceptions.DCManagerClientException(error_msg)

        kwargs['deploy_playbook'] = parsed_args.deploy_playbook

        if not os.path.isfile(parsed_args.deploy_overrides):
            error_msg = "deploy-overrides does not exist: %s" % \
                        parsed_args.deploy_overrides
            raise exceptions.DCManagerClientException(error_msg)

        kwargs['deploy_overrides'] = parsed_args.deploy_overrides

        if not os.path.isfile(parsed_args.deploy_chart):
            error_msg = "deploy-chart does not exist: %s" % \
                        parsed_args.deploy_chart
            raise exceptions.DCManagerClientException(error_msg)

        kwargs['deploy_chart'] = parsed_args.deploy_chart

        try:
            return dcmanager_client.subcloud_deploy_manager.\
                subcloud_deploy_upload(**kwargs)
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

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_deploy_manager
        return dcmanager_client.subcloud_deploy_manager.subcloud_deploy_show()
