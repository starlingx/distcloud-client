# Copyright 2015 - Huawei Technologies Co., Ltd.
# Copyright 2016 - StackStorm, Inc.
# Copyright 2016 - Ericsson AB.
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
# Copyright (c) 2017 Wind River Systems, Inc.
#
# The right to copy, distribute, modify, or otherwise make use
# of this software may be licensed only pursuant to the terms
# of an applicable Wind River license agreement.
#

import os
import tempfile
import uuid

import mock
import testtools

import osprofiler.profiler

from dcmanagerclient.api import client

AUTH_HTTP_URL = 'http://localhost:35357/v3'
AUTH_HTTPS_URL = AUTH_HTTP_URL.replace('http', 'https')
DCMANAGER_HTTP_URL = 'http://localhost:8119/v1.0'
DCMANAGER_HTTPS_URL = DCMANAGER_HTTP_URL.replace('http', 'https')
PROFILER_HMAC_KEY = 'SECRET_HMAC_KEY'
FAKE_KWARGS = {'user_domain_name': 'fake_user_domain_name',
               'user_domain_id': 'fake_user_domain_id',
               'project_domain_name': 'fake_project_domain_name',
               'project_domain_id': 'fake_project_domain_id'}


class BaseClientTests(testtools.TestCase):
    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('dcmanagerclient.api.httpclient.HTTPClient')
    def test_dcmanager_url_default(self, mock, mock_keystone_auth_session):
        keystone_session_instance = mock_keystone_auth_session.return_value
        token = keystone_session_instance.get_token.return_value = \
            str(uuid.uuid4())
        project_id = keystone_session_instance.get_project_id.return_value = \
            str(uuid.uuid4())
        user_id = keystone_session_instance.get_user_id.return_value = \
            str(uuid.uuid4())
        keystone_session_instance.get_endpoint.return_value = \
            DCMANAGER_HTTP_URL

        expected_args = (
            DCMANAGER_HTTP_URL, token, project_id, user_id)

        expected_kwargs = {
            'cacert': None,
            'insecure': False
        }

        client.client(username='dcmanager', project_name='dcmanager',
                      auth_url=AUTH_HTTP_URL, api_key='password',
                      **FAKE_KWARGS)
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('dcmanagerclient.api.httpclient.HTTPClient')
    def test_dcmanager_url_https_insecure(self, mock,
                                          mock_keystone_auth_session):
        keystone_session_instance = mock_keystone_auth_session.return_value
        token = keystone_session_instance.get_token.return_value = \
            str(uuid.uuid4())
        project_id = keystone_session_instance.get_project_id.return_value = \
            str(uuid.uuid4())
        user_id = keystone_session_instance.get_user_id.return_value = \
            str(uuid.uuid4())
        keystone_session_instance.get_endpoint.return_value = \
            DCMANAGER_HTTP_URL

        expected_args = (DCMANAGER_HTTPS_URL, token, project_id, user_id)

        expected_kwargs = {
            'cacert': None,
            'insecure': True
        }

        client.client(dcmanager_url=DCMANAGER_HTTPS_URL, username='dcmanager',
                      project_name='dcmanager', auth_url=AUTH_HTTP_URL,
                      api_key='password', cacert=None, insecure=True,
                      **FAKE_KWARGS)

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('dcmanagerclient.api.httpclient.HTTPClient')
    def test_dcmanager_url_https_secure(self, mock,
                                        mock_keystone_auth_session):
        fd, path = tempfile.mkstemp(suffix='.pem')
        keystone_session_instance = mock_keystone_auth_session.return_value
        token = keystone_session_instance.get_token.return_value = \
            str(uuid.uuid4())
        project_id = keystone_session_instance.get_project_id.return_value = \
            str(uuid.uuid4())
        user_id = keystone_session_instance.get_user_id.return_value = \
            str(uuid.uuid4())
        keystone_session_instance.get_endpoint.return_value = \
            DCMANAGER_HTTPS_URL

        expected_args = (DCMANAGER_HTTPS_URL, token, project_id, user_id)

        expected_kwargs = {
            'cacert': path,
            'insecure': False
        }

        try:
            client.client(
                dcmanager_url=DCMANAGER_HTTPS_URL,
                username='dcmanager',
                project_name='dcmanager',
                auth_url=AUTH_HTTP_URL,
                api_key='password',
                cacert=path,
                insecure=False, **FAKE_KWARGS)
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

    @mock.patch('keystoneauth1.session.Session')
    def test_dcmanager_url_https_bad_cacert(self, mock_keystone_auth_session):
        self.assertRaises(
            ValueError,
            client.client,
            dcmanager_url=DCMANAGER_HTTPS_URL,
            username='dcmanager',
            project_name='dcmanager',
            api_key='password',
            auth_url=AUTH_HTTP_URL,
            cacert='/path/to/foobar',
            insecure=False, **FAKE_KWARGS)

    @mock.patch('logging.Logger.warning')
    @mock.patch('keystoneauth1.session.Session')
    def test_dcmanager_url_https_bad_insecure(self, mock_keystone_auth_session,
                                              log_warning_mock):
        fd, path = tempfile.mkstemp(suffix='.pem')

        try:
            client.client(
                dcmanager_url=DCMANAGER_HTTPS_URL,
                username='dcmanager',
                project_name='dcmanager',
                api_key='password',
                auth_url=AUTH_HTTP_URL,
                cacert=path,
                insecure=True,
                **FAKE_KWARGS)
        finally:
            os.close(fd)
            os.unlink(path)

        self.assertTrue(log_warning_mock.called)

    @mock.patch('keystoneauth1.session.Session')
    @mock.patch('dcmanagerclient.api.httpclient.HTTPClient')
    def test_dcmanager_profile_enabled(self, mock, mock_keystone_auth_session):
        keystone_session_instance = mock_keystone_auth_session.return_value
        token = keystone_session_instance.get_token.return_value = \
            str(uuid.uuid4())
        project_id = keystone_session_instance.get_project_id.return_value = \
            str(uuid.uuid4())
        user_id = keystone_session_instance.get_user_id.return_value = \
            str(uuid.uuid4())
        keystone_session_instance.get_endpoint.return_value = \
            DCMANAGER_HTTP_URL

        expected_args = (DCMANAGER_HTTP_URL, token, project_id, user_id)

        expected_kwargs = {
            'cacert': None,
            'insecure': False
        }

        client.client(
            username='dcmanager',
            project_name='dcmanager',
            auth_url=AUTH_HTTP_URL,
            api_key='password',
            profile=PROFILER_HMAC_KEY,
            **FAKE_KWARGS)

        self.assertTrue(mock.called)
        self.assertEqual(mock.call_args[0], expected_args)
        self.assertDictEqual(mock.call_args[1], expected_kwargs)

        profiler = osprofiler.profiler.get()

        self.assertEqual(profiler.hmac_key, PROFILER_HMAC_KEY)

    def test_no_api_key(self):
        self.assertRaises(RuntimeError, client.client,
                          dcmanager_url=DCMANAGER_HTTP_URL,
                          username='dcmanager', project_name='dcmanager',
                          auth_url=AUTH_HTTP_URL, **FAKE_KWARGS)

    def test_project_name_and_project_id(self):
        self.assertRaises(RuntimeError, client.client,
                          dcmanager_url=DCMANAGER_HTTP_URL,
                          username='dcmanager', project_name='dcmanager',
                          project_id=str(uuid.uuid4()),
                          auth_url=AUTH_HTTP_URL, **FAKE_KWARGS)

    def test_user_name_and_user_id(self):
        self.assertRaises(RuntimeError, client.client,
                          dcmanager_url=DCMANAGER_HTTP_URL,
                          username='dcmanager', project_name='dcmanager',
                          user_id=str(uuid.uuid4()),
                          auth_url=AUTH_HTTP_URL, **FAKE_KWARGS)
