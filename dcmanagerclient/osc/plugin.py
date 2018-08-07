#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# Copyright (c) 2017 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

"""OpenStackClient plugin for DC Manager."""

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_DCMANAGER_API_VERSION = '1'
API_VERSION_OPTION = 'os_dcmanager_api_version'
API_NAME = 'dcmanager'
API_VERSIONS = {
    '1': 'dcmanagerclient.api.v1.client.Client',
}


def make_client(instance):
    """Return a dcmanager client."""
    version = instance._api_version[API_NAME]
    dcmanager_client = utils.get_client_class(
        API_NAME,
        version,
        API_VERSIONS)

    LOG.debug('Instantiating dcmanager client: %s', dcmanager_client)

    dcmanager_url = instance.get_endpoint_for_service_type(
        'dcmanager',
        interface='publicURL'
    )

    client = dcmanager_client(dcmanager_url=dcmanager_url,
                              session=instance.session)

    return client


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        '--os-dcmanager-api-version',
        metavar='<dcmanager-api-version>',
        default=utils.env(
            'OS_DCMANAGER_API_VERSION',
            default=DEFAULT_DCMANAGER_API_VERSION),
        help='DCMANAGER API version, default=' +
             DEFAULT_DCMANAGER_API_VERSION +
             ' (Env: OS_DCMANAGER_API_VERSION)')

    return parser
