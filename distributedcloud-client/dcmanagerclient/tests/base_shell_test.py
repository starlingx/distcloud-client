# Copyright 2015 Huawei Technologies Co., Ltd.
# Copyright 2016 Ericsson AB.
# Copyright (c) 2017, 2019, 2021, 2024 Wind River Systems, Inc.
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

import os
import sys

import six
import testtools

from dcmanagerclient import shell


class BaseShellTests(testtools.TestCase):
    def shell(self, argstr):
        orig = (sys.stdout, sys.stderr)
        clean_env = {}
        _old_env, os.environ = os.environ, clean_env.copy()

        try:
            sys.stdout = six.moves.cStringIO()
            sys.stderr = six.moves.cStringIO()
            _shell = shell.DCManagerShell()
            _shell.run(argstr.split())
        except SystemExit:
            _, exc_value, _ = sys.exc_info()
            self.assertEqual(0, exc_value.code)
        finally:
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout, sys.stderr = orig
            os.environ = _old_env

        return stdout, stderr
