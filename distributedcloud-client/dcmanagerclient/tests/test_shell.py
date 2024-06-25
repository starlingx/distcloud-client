# Copyright 2016 EricssonAB.
# Copyright (c) 2017-2021, 2024 Wind River Systems, Inc.
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

import mock

from dcmanagerclient.tests import base_shell_test as base


class TestShell(base.BaseShellTests):
    @mock.patch("dcmanagerclient.api.client.determine_client_version")
    def test_dcmanager_version(self, mock_client_version):
        self.shell("--os-dcmanager-version=v1 quota-defaults")
        self.assertTrue(mock_client_version.called)
        dcmanager_version = mock_client_version.call_args
        self.assertEqual("v1.0", dcmanager_version[0][0])

    def test_dcmanager_help(self):
        help_results = self.shell("--help")
        self.assertTrue("Commands for API" in help_results[0])

    @mock.patch("dcmanagerclient.api.client.determine_client_version")
    def test_default_dcmanager_version(self, mock_client_version):
        default_version = "v1.0"
        self.shell("quota defaults")
        self.assertTrue(mock_client_version.called)
        dcmanager_version = mock_client_version.call_args
        self.assertEqual(default_version, dcmanager_version[0][0])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_env_variables(self, mock_client):
        self.shell(
            "--os-auth-url=https://127.0.0.1:35357/v3 "
            "--os-username=admin "
            "--os-password=1234 "
            "--os-tenant-name=admin "
            "quota defaults"
        )
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("https://127.0.0.1:35357/v3", params[1]["auth_url"])
        self.assertEqual("admin", params[1]["username"])
        self.assertEqual("admin", params[1]["project_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_env_without_auth_url(self, mock_client):
        self.shell(
            "--os-username=admin "
            "--os-password=1234 "
            "--os-tenant-name=admin "
            "quota defaults"
        )
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("", params[1]["auth_url"])
        self.assertEqual("admin", params[1]["username"])
        self.assertEqual("admin", params[1]["project_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_kb_service_type(self, mock_client):
        self.shell("--os-service-type=dcmanager")
        self.assertTrue(mock_client.called)
        parameters = mock_client.call_args
        self.assertEqual("dcmanager", parameters[1]["service_type"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_kb_default_service_type(self, mock_client):
        self.shell("quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        # Default service type is dcmanager
        self.assertEqual("dcmanager", params[1]["service_type"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_kb_endpoint_type(self, mock_client):
        self.shell("--os-endpoint-type=adminURL quota-defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("adminURL", params[1]["endpoint_type"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_kb_default_endpoint_type(self, mock_client):
        self.shell("quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("internalURL", params[1]["endpoint_type"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_os_auth_token(self, mock_client):
        self.shell("--os-auth-token=abcd1234 quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("abcd1234", params[1]["auth_token"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_command_without_dcmanager_url(self, mock_client):
        self.shell("quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("", params[1]["dcmanager_url"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_command_with_dcmanager_url(self, mock_client):
        self.shell("--dcmanager-url=http://localhost:8118/v1.0 quota-defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("http://localhost:8118/v1.0", params[1]["dcmanager_url"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_command_without_project_name(self, mock_client):
        self.shell("quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("", params[1]["project_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_profile(self, mock_client):
        self.shell("--profile=SECRET_HMAC_KEY quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("SECRET_HMAC_KEY", params[1]["profile"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_without_profile(self, mock_client):
        self.shell("quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual(None, params[1]["profile"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_project_name(self, mock_client):
        self.shell("--os-project-name default quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("default", params[1]["project_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_tenant_name(self, mock_client):
        self.shell("--os-tenant-name default quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("default", params[1]["project_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_project_domain_name(self, mock_client):
        self.shell("--os-project-domain-name default quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("default", params[1]["project_domain_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_project_domain_id(self, mock_client):
        self.shell("--os-project-domain-id default quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("default", params[1]["project_domain_id"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_user_domain_name(self, mock_client):
        self.shell("--os-user-domain-name default quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("default", params[1]["user_domain_name"])

    @mock.patch("dcmanagerclient.api.client.client")
    def test_dcmanager_user_domain_id(self, mock_client):
        self.shell("--os-user-domain-id default quota defaults")
        self.assertTrue(mock_client.called)
        params = mock_client.call_args
        self.assertEqual("default", params[1]["user_domain_id"])
