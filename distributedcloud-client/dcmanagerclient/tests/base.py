# Copyright 2013 - Mirantis, Inc.
# Copyright 2016 - Ericsson AB.
# Copyright (c) 2017-2021 Wind River Systems, Inc.
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

import json

import mock
from oslo_utils import timeutils
import testtools

from dcmanagerclient.api import base as api_base


# Subcloud sample data
BOOTSTRAP_ADDRESS = '10.10.10.12'
TIME_NOW = timeutils.utcnow().isoformat()
ID = '1'
ID_1 = '2'
NAME = 'subcloud1'
SYSTEM_MODE = "duplex"
DESCRIPTION = 'subcloud1 description'
LOCATION = 'subcloud1 location'
SOFTWARE_VERSION = '12.34'
MANAGEMENT_STATE = 'unmanaged'
AVAILABILITY_STATUS = 'offline'
DEPLOY_STATUS = 'not-deployed'
SYNC_STATUS = 'unknown'
ERROR_DESCRIPTION = 'No errors present'
REGION_NAME = '2ec93dfb654846909efe61d1b39dd2ce'
DEPLOY_STATE_PRE_DEPLOY = 'pre-deploy'
DEPLOY_STATE_PRE_RESTORE = 'pre-restore'
MANAGEMENT_SUBNET = '192.168.101.0/24'
MANAGEMENT_START_IP = '192.168.101.2'
MANAGEMENT_END_IP = '192.168.101.50'
MANAGEMENT_GATEWAY_IP = '192.168.101.1'
SYSTEMCONTROLLER_GATEWAY_IP = '192.168.204.101'
EXTERNAL_OAM_SUBNET = "10.10.10.0/24"
EXTERNAL_OAM_GATEWAY_ADDRESS = "10.10.10.1"
EXTERNAL_OAM_FLOATING_ADDRESS = "10.10.10.12"
DEFAULT_SUBCLOUD_GROUP_ID = '1'
DEPLOY_CONFIG_SYNC_STATUS = 'Deployment: configurations up-to-date'
SUBCLOUD_REHOME_DATA = None
BACKUP_STATUS = 'None'
BACKUP_DATETIME = 'None'

# Useful for subcloud name configuration
NAME_SC2 = "subcloud2"
SET_FIELD_VALUE_DICT = {
    "region_name": None
}

# Subcloud CLI resource object
SUBCLOUD_RESOURCE = api_base.Subcloud(
    mock,
    subcloud_id=ID,
    name=NAME,
    description=DESCRIPTION,
    location=LOCATION,
    software_version=SOFTWARE_VERSION,
    management_state=MANAGEMENT_STATE,
    availability_status=AVAILABILITY_STATUS,
    deploy_status=DEPLOY_STATUS,
    error_description=ERROR_DESCRIPTION,
    management_subnet=MANAGEMENT_SUBNET,
    management_start_ip=MANAGEMENT_START_IP,
    management_end_ip=MANAGEMENT_END_IP,
    management_gateway_ip=MANAGEMENT_GATEWAY_IP,
    systemcontroller_gateway_ip=SYSTEMCONTROLLER_GATEWAY_IP,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
    group_id=DEFAULT_SUBCLOUD_GROUP_ID,
    backup_status=BACKUP_STATUS,
    backup_datetime=BACKUP_DATETIME)

# Subcloud CLI resource object with peerid rehome data
SUBCLOUD_RESOURCE_WITH_PEERID_REHOME_DATA = api_base.Subcloud(
    mock,
    subcloud_id=ID,
    name=NAME,
    description=DESCRIPTION,
    location=LOCATION,
    software_version=SOFTWARE_VERSION,
    management_state=MANAGEMENT_STATE,
    availability_status=AVAILABILITY_STATUS,
    deploy_status=DEPLOY_STATUS,
    management_subnet=MANAGEMENT_SUBNET,
    management_start_ip=MANAGEMENT_START_IP,
    management_end_ip=MANAGEMENT_END_IP,
    management_gateway_ip=MANAGEMENT_GATEWAY_IP,
    systemcontroller_gateway_ip=SYSTEMCONTROLLER_GATEWAY_IP,
    group_id=DEFAULT_SUBCLOUD_GROUP_ID,
    rehome_data=SUBCLOUD_REHOME_DATA,
    created_at=TIME_NOW,
    updated_at=TIME_NOW,
    backup_status=BACKUP_STATUS,
    backup_datetime=BACKUP_DATETIME)

# Subcloud result values returned from various API calls (e.g. subcloud show)
SUBCLOUD_FIELD_RESULT_LIST = (
    ID,
    NAME,
    DESCRIPTION,
    LOCATION,
    SOFTWARE_VERSION,
    MANAGEMENT_STATE,
    AVAILABILITY_STATUS,
    DEPLOY_STATUS,
    MANAGEMENT_SUBNET,
    MANAGEMENT_START_IP,
    MANAGEMENT_END_IP,
    MANAGEMENT_GATEWAY_IP,
    SYSTEMCONTROLLER_GATEWAY_IP,
    DEFAULT_SUBCLOUD_GROUP_ID,
    TIME_NOW,
    TIME_NOW,
    BACKUP_STATUS,
    BACKUP_DATETIME
)

# Subcloud result values returned from various API calls (e.g. subcloud show)
SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA = (
    ID,
    NAME,
    DESCRIPTION,
    LOCATION,
    SOFTWARE_VERSION,
    MANAGEMENT_STATE,
    AVAILABILITY_STATUS,
    DEPLOY_STATUS,
    MANAGEMENT_SUBNET,
    MANAGEMENT_START_IP,
    MANAGEMENT_END_IP,
    MANAGEMENT_GATEWAY_IP,
    SYSTEMCONTROLLER_GATEWAY_IP,
    DEFAULT_SUBCLOUD_GROUP_ID,
    SUBCLOUD_REHOME_DATA,
    TIME_NOW,
    TIME_NOW,
    BACKUP_STATUS,
    BACKUP_DATETIME
)
EMPTY_SUBCLOUD_FIELD_RESULT = (('<none>',) * len(SUBCLOUD_FIELD_RESULT_LIST),)
EMPTY_SUBCLOUD_FIELD_RESULT_WITH_PEERID_REHOME_DATA = \
    (('<none>',) * len(SUBCLOUD_FIELD_RESULT_LIST_WITH_PEERID_REHOME_DATA),)

# Subcloud result values returned from subcloud list command
SUBCLOUD_LIST_RESULT = (
    ID,
    NAME,
    MANAGEMENT_STATE,
    AVAILABILITY_STATUS,
    DEPLOY_STATUS,
    SYNC_STATUS,
    BACKUP_STATUS,
    BACKUP_DATETIME
)

EMPTY_SUBCLOUD_LIST_RESULT = (('<none>',) * len(SUBCLOUD_LIST_RESULT),)

FAKE_BOOTSTRAP_VALUES = {
    "system_mode": SYSTEM_MODE,
    "name": NAME,
    "description": DESCRIPTION,
    "location": LOCATION,
    "management_subnet": MANAGEMENT_SUBNET,
    "management_start_address": MANAGEMENT_START_IP,
    "management_end_address": MANAGEMENT_END_IP,
    "management_gateway_address": MANAGEMENT_GATEWAY_IP,
    "external_oam_subnet": EXTERNAL_OAM_SUBNET,
    "external_oam_gateway_address": EXTERNAL_OAM_GATEWAY_ADDRESS,
    "external_oam_floating_address": EXTERNAL_OAM_FLOATING_ADDRESS,
    'backup_status': BACKUP_STATUS,
    'backup_datetime': BACKUP_DATETIME,
    'backup_status': BACKUP_STATUS,
    'backup_datetime': BACKUP_DATETIME
}

FAKE_INSTALL_VALUES = {
    "image": "http://192.168.101.2:8080/iso/bootimage.iso",
    "software_version": SOFTWARE_VERSION,
    "bootstrap_interface": "eno1",
    "bootstrap_address": "128.224.151.183",
    "bootstrap_address_prefix": 23,
    "bmc_address": "128.224.64.180",
    "bmc_username": "root",
    "nexthop_gateway": "128.224.150.1",
    "network_address": "128.224.144.0",
    "network_mask": "255.255.254.0",
    "install_type": 3,
    "console_type": "tty0",
    "bootstrap_vlan": 128,
    "rootfs_device": "/dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0",
    "boot_device": "/dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0",
    "rd.net.timeout.ipv6dad": 300,
}


class FakeResponse(object):
    """Fake response for testing DC Manager Client."""

    def __init__(self, status_code, content=None):
        self.status_code = status_code
        self.content = content
        self.headers = {}
        self.text = ''

    def json(self):
        return json.loads(self.content)


class BaseClientTest(testtools.TestCase):
    _client = None

    def setUp(self):
        super(BaseClientTest, self).setUp()

    def mock_http_get(self, content, status_code=200):
        if isinstance(content, dict):
            content = json.dumps(content)

        self._client.http_client.get = mock.MagicMock(
            return_value=FakeResponse(status_code, content))

        return self._client.http_client.get

    def mock_http_post(self, content, status_code=201):
        if isinstance(content, dict):
            content = json.dumps(content)

        self._client.http_client.post = mock.MagicMock(
            return_value=FakeResponse(status_code, content))

        return self._client.http_client.post

    def mock_http_put(self, content, status_code=200):
        if isinstance(content, dict):
            content = json.dumps(content)

        self._client.http_client.put = mock.MagicMock(
            return_value=FakeResponse(status_code, content))

        return self._client.http_client.put

    def mock_http_delete(self, status_code=204):
        self._client.http_client.delete = mock.MagicMock(
            return_value=FakeResponse(status_code))

        return self._client.http_client.delete


class BaseCommandTest(testtools.TestCase):
    def setUp(self):
        super(BaseCommandTest, self).setUp()
        self.app = mock.Mock()
        self.client = self.app.client_manager.subcloud_manager

    def call(self, command, app_args=None, prog_name=''):
        if app_args is None:
            app_args = []
        cmd = command(self.app, app_args)

        parsed_args = cmd.get_parser(prog_name).parse_args(app_args)

        return cmd.take_action(parsed_args)
