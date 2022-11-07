# Copyright 2016 - Ericsson AB
# Copyright 2015 - Huawei Technologies Co. Ltd
# Copyright 2015 - StackStorm, Inc.
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

import getpass
import json
import os
import yaml

from six.moves.urllib import parse
from six.moves.urllib import request

from dcmanagerclient import exceptions


def do_action_on_many(action, resources, success_msg, error_msg):
    """Helper to run an action on many resources."""
    failure_flag = False

    for resource in resources:
        try:
            action(resource)
            print(success_msg % resource)
        except Exception as e:
            failure_flag = True
            print(e)

    if failure_flag:
        raise exceptions.DCManagerClientException(error_msg)


def load_content(content):
    if content is None or content == '':
        return dict()

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
        error_msg = "Error: %s is a directory." % contents_or_file_name
        raise exceptions.DCManagerClientException(error_msg)

    try:
        if parse.urlparse(contents_or_file_name).scheme:
            definition_url = contents_or_file_name
        else:
            path = os.path.abspath(contents_or_file_name)
            definition_url = parse.urljoin(
                'file:',
                request.pathname2url(path)
            )
        return request.urlopen(definition_url).read().decode('utf8')
    except Exception as e:
        raise exceptions.DCManagerClientException(
            "Error: Could not open file %s: %s" % (contents_or_file_name, e))


def prompt_for_password(password_type='sysadmin'):
    while True:
        try:
            password = getpass.getpass(
                "Enter the " + password_type + " password for the subcloud: ")
            if len(password) < 1:
                print("Password cannot be empty")
                continue

            confirm = getpass.getpass(
                "Re-enter " + password_type + " password to confirm: ")
            if password != confirm:
                print("Passwords did not match")
                continue
            break
        except KeyboardInterrupt:
            raise exceptions.DCManagerClientException(
                "\nPassword prompt interrupted."
            )
    return password
