# Copyright 2016 - Ericsson AB
# Copyright 2015 - Huawei Technologies Co. Ltd
# Copyright 2015 - StackStorm, Inc.
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

import getpass
import json
import os
import base64
from urllib import parse, request

import yaml

from dcmanagerclient import exceptions


def do_action_on_many(action, resources, success_msg, error_msg):
    """Helper to run an action on many resources."""
    failure_flag = False

    for resource in resources:
        try:
            action(resource)
            print(success_msg % resource)
        except Exception as exc:
            failure_flag = True
            print(exc)

    if failure_flag:
        raise exceptions.DCManagerClientException(error_msg)


def load_content(content):
    if content is None or content == "":
        return {}

    try:
        data = yaml.safe_load(content)
    except Exception:
        data = json.loads(content)

    return data


def get_contents_if_file(contents_or_file_name):
    """Get the contents of a file.

    If the value passed in is a file name or file URI, return the
    contents. If not, or there is an error reading the file contents,
    raise an exception.

    """
    if os.path.isdir(contents_or_file_name):
        error_msg = f"Error: {contents_or_file_name} is a directory."
        raise exceptions.DCManagerClientException(error_msg)

    try:
        if parse.urlparse(contents_or_file_name).scheme:
            definition_url = contents_or_file_name
        else:
            path = os.path.abspath(contents_or_file_name)
            definition_url = parse.urljoin("file:", request.pathname2url(path))
        return request.urlopen(definition_url).read().decode("utf8")
    except Exception as exc:
        raise exceptions.DCManagerClientException(
            f"Error: Could not open file {contents_or_file_name}: {exc}"
        )


def prompt_for_password(password_type="sysadmin", item_type="subcloud"):
    while True:
        try:
            password = getpass.getpass(
                f"Enter the {password_type} password for the {item_type}: "
            )
            if len(password) < 1:
                print("Password cannot be empty")
                continue

            confirm = getpass.getpass(f"Re-enter {password_type} password to confirm: ")
            if password != confirm:
                print("Passwords did not match")
                continue
            break
        except KeyboardInterrupt as exc:
            raise exceptions.DCManagerClientException(
                "\nPassword prompt interrupted."
            ) from exc
    return password


def subcloud_detail_format(subcloud=None):
    columns = (
        "id",
        "name",
        "description",
        "location",
        "software_version",
        "management",
        "availability",
        "deploy_status",
        "management_subnet",
        "management_start_ip",
        "management_end_ip",
        "management_gateway_ip",
        "systemcontroller_gateway_ip",
        "group_id",
        "peer_group_id",
        "created_at",
        "updated_at",
        "backup_status",
        "backup_datetime",
        "prestage_status",
        "prestage_versions",
    )

    if subcloud:
        data = (
            subcloud.subcloud_id,
            subcloud.name,
            subcloud.description,
            subcloud.location,
            subcloud.software_version,
            subcloud.management_state,
            subcloud.availability_status,
            subcloud.deploy_status,
            subcloud.management_subnet,
            subcloud.management_start_ip,
            subcloud.management_end_ip,
            subcloud.management_gateway_ip,
            subcloud.systemcontroller_gateway_ip,
            subcloud.group_id,
            subcloud.peer_group_id,
            subcloud.created_at,
            subcloud.updated_at,
            subcloud.backup_status,
            subcloud.backup_datetime,
            subcloud.prestage_status,
            subcloud.prestage_versions,
        )

        for _, sync_status in enumerate(subcloud.endpoint_sync_status):
            added_field = (sync_status["endpoint_type"] + "_sync_status",)
            added_value = (sync_status["sync_status"],)
            columns += tuple(added_field)
            data += tuple(added_value)

        if subcloud.oam_floating_ip != "unavailable":
            columns += ("oam_floating_ip",)
            data += (subcloud.oam_floating_ip,)
    else:
        data = (("<none>",) * len(columns),)

    return columns, data


def set_sysadmin_password(parsed_args, data):
    if parsed_args.sysadmin_password:
        data["sysadmin_password"] = base64.b64encode(
            parsed_args.sysadmin_password.encode("utf-8")
        )
    else:
        password = prompt_for_password()
        data["sysadmin_password"] = base64.b64encode(password.encode("utf-8"))
