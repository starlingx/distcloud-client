# Copyright (c) 2016 Ericsson AB
# Copyright (c) 2017-2024 Wind River Systems, Inc.
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

import requests
from bs4 import BeautifulSoup

from dcmanagerclient import exceptions
from dcmanagerclient.api import httpclient


class Resource:
    # This will be overridden by the actual resource
    resource_name = "Something"


class Subcloud(Resource):
    resource_name = "subclouds"

    _PAYLOAD_NAME_MAP = {
        "id": "subcloud_id",
        "name": "name",
        "description": "description",
        "location": "location",
        "software-version": "software_version",
        "management-state": "management_state",
        "availability-status": "availability_status",
        "deploy-status": "deploy_status",
        "error-description": "error_description",
        "management-subnet": "management_subnet",
        "management-start-ip": "management_start_ip",
        "management-end-ip": "management_end_ip",
        "management-gateway-ip": "management_gateway_ip",
        "systemcontroller-gateway-ip": "systemcontroller_gateway_ip",
        "created-at": "created_at",
        "updated-at": "updated_at",
        "group_id": "group_id",
        "peer_group_id": "peer_group_id",
        "rehome_data": "rehome_data",
        "sync_status": "sync_status",
        "endpoint_sync_status": "endpoint_sync_status",
        "backup-status": "backup_status",
        "backup-datetime": "backup_datetime",
        "prestage-software-version": "prestage_software_version",
        "prestage-status": "prestage_status",
        "prestage-versions": "prestage_versions",
        "region-name": "region_name",
        "info_message": "info_message",
    }

    def __init__(
        self,
        manager,
        subcloud_id,
        name,
        description,
        location,
        software_version,
        management_state,
        availability_status,
        deploy_status,
        management_subnet,
        management_start_ip,
        management_end_ip,
        management_gateway_ip,
        systemcontroller_gateway_ip,
        created_at,
        updated_at,
        group_id,
        sync_status="unknown",
        endpoint_sync_status=None,
        backup_status=None,
        backup_datetime=None,
        error_description=None,
        prestage_software_version=None,
        peer_group_id=None,
        rehome_data=None,
        region_name=None,
        prestage_status=None,
        prestage_versions=None,
        info_message=None,
    ):
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
        self.deploy_config_sync_status = "unknown"
        self.management_start_ip = management_start_ip
        self.management_end_ip = management_end_ip
        self.management_gateway_ip = management_gateway_ip
        self.systemcontroller_gateway_ip = systemcontroller_gateway_ip
        self.created_at = created_at
        self.updated_at = updated_at
        self.group_id = group_id
        self.peer_group_id = peer_group_id
        self.rehome_data = rehome_data
        self.sync_status = sync_status
        self.endpoint_sync_status = endpoint_sync_status
        self.backup_status = backup_status
        self.backup_datetime = backup_datetime
        self.prestage_software_version = prestage_software_version
        self.region_name = region_name
        self.prestage_status = prestage_status
        self.prestage_versions = prestage_versions
        self.info_message = info_message

    @classmethod
    def from_payload(cls, manager, payload):
        """Returns a class instance based on a single payload."""
        parameters = {"manager": manager}

        # Converts payload parameter name to match the class attributes
        for payload_param, value in payload.items():
            param_name = cls._PAYLOAD_NAME_MAP.get(payload_param)
            if param_name is not None:
                parameters[param_name] = value

        subcloud = cls(**parameters)
        return subcloud

    @classmethod
    def from_payloads(cls, manager, payloads):
        """Returns a list of class instances from a payload list."""
        subclouds = []
        for payload in payloads:
            subcloud = cls.from_payload(manager, payload)
            subclouds.append(subcloud)
        return subclouds


class ResourceManager:
    resource_class = None

    def __init__(self, http_client: httpclient.HTTPClient):
        self.http_client = http_client

    def _generate_resource(self, json_response_key):
        json_objects = [json_response_key[item] for item in json_response_key]
        resource = []
        for json_object in json_objects:
            for resource_data in json_object:
                resource.append(
                    self.resource_class(  # pylint: disable=not-callable
                        self, resource_data, json_object[resource_data]
                    )
                )
        return resource

    def _list(self, url, _response_key=None):
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
            data = json_object.get("usage")
            for values in data:
                resource.append(
                    self.resource_class(  # pylint: disable=not-callable
                        self,
                        values,
                        json_object["limits"][values],
                        json_object["usage"][values],
                    )
                )
        return resource

    def _delete(self, url):
        resp = self.http_client.delete(url)
        if resp.status_code != 200:
            self._raise_api_exception(resp)

    def _raise_api_exception(self, resp: requests.Response):
        # Handle 500 status code with empty content which is returned by
        # unhandled exceptions on the server side
        if resp.status_code == 500 and not resp.content:
            error_message = (
                "The server has either erred or is incapable "
                "of performing the requested operation."
            )
            raise exceptions.APIException(
                error_code=resp.status_code, error_message=error_message
            )

        # Otherwise attempt to parse the HTML response content
        try:
            soup = BeautifulSoup(resp.content, "html.parser")
            line_list = soup.body.get_text().strip().split("\n")

            # Remove any leading/trailing whitespace and empty lines
            line_list = [line.strip() for line in line_list if line.strip()]

            # Extract explanation and detail messages
            explanation = line_list[1] if len(line_list) > 1 else line_list[0]
            details = "\n".join(line_list[2:]) if len(line_list) > 2 else None

            # Ensure explanation ends with a period
            if not explanation.endswith("."):
                explanation += "."

            # Build the error message
            error_msg = explanation
            if details:
                error_msg = f"{error_msg}\nDetails: {details.strip()}"

        except Exception:
            # Fallback to raw content in case of parsing errors
            error_msg = resp.content.decode("utf-8", errors="ignore")

        raise exceptions.APIException(
            error_code=resp.status_code, error_message=error_msg
        )


def get_json(response):
    """Get JSON representation of response."""
    json_field_or_function = getattr(response, "json", None)
    if callable(json_field_or_function):
        return response.json()
    return json.loads(response.content)
