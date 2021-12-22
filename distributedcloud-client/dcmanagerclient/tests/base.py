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
import testtools


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
