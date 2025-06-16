# Copyright 2015 - StackStorm, Inc.
# Copyright (c) 2017, 2019, 2021, 2024-2025 Wind River Systems, Inc.
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
import os
import tarfile
import tempfile

import testtools
import yaml

from dcmanagerclient import exceptions, utils

ENV_DICT = {"k1": "abc", "k2": 123, "k3": True}
ENV_STR = json.dumps(ENV_DICT)
ENV_YAML = yaml.safe_dump(ENV_DICT, default_flow_style=False)


class UtilityTest(testtools.TestCase):
    def test_load_empty(self):
        self.assertDictEqual({}, utils.load_content(None))
        self.assertDictEqual({}, utils.load_content(""))
        self.assertDictEqual({}, utils.load_content("{}"))
        self.assertListEqual([], utils.load_content("[]"))

    def test_load_json_content(self):
        self.assertDictEqual(ENV_DICT, utils.load_content(ENV_STR))

    def test_load_yaml_content(self):
        self.assertDictEqual(ENV_DICT, utils.load_content(ENV_YAML))

    def test_validate_cloud_init_config_file_not_exists(self):
        self.assertRaises(
            exceptions.DCManagerClientException,
            utils.validate_cloud_init_config,
            "/nonexistent/file.tar",
        )

    def test_validate_cloud_init_config_invalid_tar(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"not a tar file")
            f.flush()
            try:
                self.assertRaises(
                    exceptions.DCManagerClientException,
                    utils.validate_cloud_init_config,
                    f.name,
                )
            finally:
                os.unlink(f.name)

    def test_validate_cloud_init_config_valid_tar(self):
        with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as f:
            try:
                with tarfile.open(f.name, "w") as tar:
                    info = tarfile.TarInfo(name="test.txt")
                    info.size = 4
                    tar.addfile(info, fileobj=None)
                utils.validate_cloud_init_config(f.name)
            finally:
                os.unlink(f.name)
