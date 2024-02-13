# Copyright 2016 - StackStorm, Inc.
# Copyright 2016 - Ericsson AB.
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

import copy
import uuid

import mock
from osprofiler import _utils as osprofiler_utils
import osprofiler.profiler
import requests
import testtools

from dcmanagerclient.api import httpclient

API_BASE_URL = "http://localhost:8119/v1.0"
API_URL = "/os-quota-sets"

EXPECTED_URL = API_BASE_URL + API_URL

AUTH_TOKEN = str(uuid.uuid4())
PROJECT_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
PROFILER_HMAC_KEY = "SECRET_HMAC_KEY"
PROFILER_TRACE_ID = str(uuid.uuid4())

EXPECTED_AUTH_HEADERS = {
    "x-auth-token": AUTH_TOKEN,
    "X-Project-Id": PROJECT_ID,
    "X-User-Id": USER_ID,
}

EXPECTED_REQ_OPTIONS = {"headers": EXPECTED_AUTH_HEADERS}

EXPECTED_BODY = {"k1": "abc", "k2": 123, "k3": True}


class FakeRequest(object):
    def __init__(self, method):
        self.method = method


class FakeResponse(object):
    def __init__(self, method, url, status_code):
        self.request = FakeRequest(method)
        self.url = url
        self.status_code = status_code
        self.text = ""


class HTTPClientTest(testtools.TestCase):
    def setUp(self):
        super(HTTPClientTest, self).setUp()
        osprofiler.profiler.init(None)
        self.client = httpclient.HTTPClient(
            API_BASE_URL, AUTH_TOKEN, PROJECT_ID, USER_ID
        )

    @mock.patch.object(requests, "get")
    def test_get_request_options(self, mock_requests_get):
        osprofiler.profiler.clean()
        self.client.get(API_URL)

        mock_requests_get.return_value = FakeResponse("get", EXPECTED_URL, 200)
        mock_requests_get.assert_called_with(EXPECTED_URL, **EXPECTED_REQ_OPTIONS)

    @mock.patch.object(requests, "get")
    def test_get_request_options_with_headers_for_get(self, mock_requests_get):
        headers = {"foo": "bar"}

        self.client.get(API_URL, headers=headers)
        mock_requests_get.return_value = FakeResponse("get", EXPECTED_URL, 200)

        expected_options = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        expected_options["headers"].update(headers)

        mock_requests_get.assert_called_with(EXPECTED_URL, **expected_options)

    @mock.patch.object(osprofiler.profiler._Profiler, "get_base_id")
    @mock.patch.object(osprofiler.profiler._Profiler, "get_id")
    @mock.patch.object(requests, "get")
    def test_get_request_options_with_profile_enabled(
        self, mock_requests_get, mock_profiler_get_id, mock_profiler_get_base_id
    ):
        osprofiler.profiler.clean()
        osprofiler.profiler.init(PROFILER_HMAC_KEY)

        mock_requests_get.return_value = FakeResponse("get", EXPECTED_URL, 200)
        mock_profiler_get_id.return_value = PROFILER_TRACE_ID
        mock_profiler_get_base_id.return_value = PROFILER_TRACE_ID

        data = {"base_id": PROFILER_TRACE_ID, "parent_id": PROFILER_TRACE_ID}
        signed_data = osprofiler_utils.signed_pack(data, PROFILER_HMAC_KEY)
        headers = {"X-Trace-Info": signed_data[0], "X-Trace-HMAC": signed_data[1]}
        self.client.get(API_URL)

        expected_options = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        expected_options["headers"].update(headers)

        mock_requests_get.assert_called_with(EXPECTED_URL, **expected_options)

    @mock.patch.object(requests, "post")
    def test_get_request_options_with_headers_for_post(self, mock_requests_post):
        headers = {"foo": "bar"}

        self.client.post(API_URL, EXPECTED_BODY, headers=headers)
        mock_requests_post.return_value = FakeResponse("post", EXPECTED_URL, 201)

        expected_options = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        expected_options["headers"].update(headers)
        expected_options["headers"]["content-type"] = "application/json"

        mock_requests_post.assert_called_with(
            EXPECTED_URL, EXPECTED_BODY, **expected_options
        )

    @mock.patch.object(requests, "put")
    def test_get_request_options_with_headers_for_put(self, mock_requests_put):
        headers = {"foo": "bar"}

        self.client.put(API_URL, EXPECTED_BODY, headers=headers)
        mock_requests_put.return_value = FakeResponse("put", EXPECTED_URL, 200)

        expected_options = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        expected_options["headers"].update(headers)
        expected_options["headers"]["content-type"] = "application/json"

        mock_requests_put.assert_called_with(
            EXPECTED_URL, EXPECTED_BODY, **expected_options
        )

    @mock.patch.object(requests, "delete")
    def test_get_request_options_with_headers_for_delete(self, mock_requests_delete):
        headers = {"foo": "bar"}

        self.client.delete(API_URL, headers=headers)
        mock_requests_delete.return_value = FakeResponse("delete", EXPECTED_URL, 200)

        expected_options = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        expected_options["headers"].update(headers)

        mock_requests_delete.assert_called_with(EXPECTED_URL, **expected_options)

    @mock.patch.object(httpclient.HTTPClient, "_get_request_options")
    @mock.patch.object(requests, "get")
    def test_http_get(self, mock_requests_get, mock_get_request_options):
        self.client.get(API_URL)
        mock_requests_get.return_value = FakeResponse("get", EXPECTED_URL, 200)
        mock_get_request_options.return_value = copy.deepcopy(EXPECTED_REQ_OPTIONS)

        mock_get_request_options.assert_called_with("get", None)
        mock_requests_get.assert_called_with(EXPECTED_URL)

    @mock.patch.object(httpclient.HTTPClient, "_get_request_options")
    @mock.patch.object(requests, "post")
    def test_http_post(self, mock_requests_post, mock_get_request_options):
        self.client.post(API_URL, EXPECTED_BODY)
        mock_get_request_options.return_value = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        mock_requests_post.return_value = FakeResponse("post", EXPECTED_URL, 201)

        mock_get_request_options.assert_called_with("post", None)
        mock_requests_post.assert_called_with(EXPECTED_URL, EXPECTED_BODY)

    @mock.patch.object(httpclient.HTTPClient, "_get_request_options")
    @mock.patch.object(requests, "put")
    def test_http_put(self, mock_requests_put, mock_get_request_options):
        self.client.put(API_URL, EXPECTED_BODY)
        mock_get_request_options.return_value = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        mock_requests_put.return_value = FakeResponse("put", EXPECTED_URL, 200)

        mock_get_request_options.assert_called_with("put", None)
        mock_requests_put.assert_called_with(EXPECTED_URL, EXPECTED_BODY)

    @mock.patch.object(httpclient.HTTPClient, "_get_request_options")
    @mock.patch.object(requests, "delete")
    def test_http_delete(self, mock_requests_delete, mock_get_request_options):
        self.client.delete(API_URL)
        mock_get_request_options.return_value = copy.deepcopy(EXPECTED_REQ_OPTIONS)
        mock_requests_delete.return_value = FakeResponse("delete", EXPECTED_URL, 200)

        mock_get_request_options.assert_called_with("delete", None)
        mock_requests_delete.assert_called_with(EXPECTED_URL)
