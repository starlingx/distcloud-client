# Copyright (c) 2016 Ericsson AB
# Copyright (c) 2017-2022 Wind River Systems, Inc.
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

from bs4 import BeautifulSoup
import json

from dcmanagerclient import exceptions


class Resource(object):
    # This will be overridden by the actual resource
    resource_name = 'Something'


class Subcloud(Resource):
    resource_name = 'subclouds'

    def __init__(self, manager, subcloud_id, name, description, location,
                 software_version, management_state, availability_status,
                 deploy_status, error_description,
                 management_subnet, management_start_ip, management_end_ip,
                 management_gateway_ip, systemcontroller_gateway_ip,
                 created_at, updated_at, group_id, sync_status="unknown",
                 endpoint_sync_status=None, backup_status=None,
                 backup_datetime=None):
        if endpoint_sync_status is None:
            endpoint_sync_status = {}
        self.manager = manager
        self.subcloud_id = subcloud_id
        self.name = name
        self.description = description
        self.location = location
        self.software_version = software_version
        self.management_subnet = management_subnet
        self.management_state = management_state
        self.availability_status = availability_status
        self.deploy_status = deploy_status
        self.error_description = error_description
        self.oam_floating_ip = "unavailable"
        self.management_start_ip = management_start_ip
        self.management_end_ip = management_end_ip
        self.management_gateway_ip = management_gateway_ip
        self.systemcontroller_gateway_ip = systemcontroller_gateway_ip
        self.created_at = created_at
        self.updated_at = updated_at
        self.group_id = group_id
        self.sync_status = sync_status
        self.endpoint_sync_status = endpoint_sync_status
        self.backup_status = backup_status
        self.backup_datetime = backup_datetime


class ResourceManager(object):
    resource_class = None

    def __init__(self, http_client):
        self.http_client = http_client

    def _generate_resource(self, json_response_key):
        json_objects = [json_response_key[item] for item in json_response_key]
        resource = []
        for json_object in json_objects:
            for resource_data in json_object:
                resource.append(
                    self.resource_class(  # pylint: disable=not-callable
                        self,
                        resource_data,
                        json_object[resource_data]))
        return resource

    def _list(self, url, response_key=None):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        resource = self._generate_resource(json_response_key)
        return resource

    def _update(self, url, data):
        data = json.dumps(data)
        resp = self.http_client.put(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        result = self._generate_resource(json_response_key)
        return result

    def _sync(self, url, data=None):
        resp = self.http_client.put(url, data)
        if resp.status_code != 200:
            self._raise_api_exception(resp)

    def _detail(self, url):
        resp = self.http_client.get(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_response_key = get_json(resp)
        json_objects = [json_response_key[item] for item in json_response_key]
        resource = []
        for json_object in json_objects:
            data = json_object.get('usage')
            for values in data:
                resource.append(
                    self.resource_class(  # pylint: disable=not-callable
                        self,
                        values,
                        json_object['limits'][values],
                        json_object['usage'][values]))
        return resource

    def _delete(self, url):
        resp = self.http_client.delete(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)

    def _raise_api_exception(self, resp):
        error_html = resp.content
        soup = BeautifulSoup(error_html, 'html.parser')
        # Get the raw html with get_text, strip out the blank lines on
        # front and back, then get rid of the 2 lines of error code number
        # and error code explanation so that we are left with just the
        # meaningful error text.
        try:
            error_msg = soup.body.get_text().lstrip().rstrip().split('\n')[2]
        except Exception:
            error_msg = resp.content

        raise exceptions.APIException(error_code=resp.status_code,
                                      error_message=error_msg)


def get_json(response):
    """Get JSON representation of response."""
    json_field_or_function = getattr(response, 'json', None)
    if callable(json_field_or_function):
        return response.json()
    else:
        return json.loads(response.content)
