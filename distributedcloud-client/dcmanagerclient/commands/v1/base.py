# Copyright (c) 2016 Ericsson AB
# Copyright (c) 2017, 2019, 2021-2022, 2024 Wind River Systems, Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#

import abc

import six
from osc_lib.command import command


@six.add_metaclass(abc.ABCMeta)
class DCManagerLister(command.Lister):
    @abc.abstractmethod
    def _get_format_function(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_resources(self, parsed_args):
        """Get a list of API resources (e.g. using client)."""
        raise NotImplementedError

    def _validate_parsed_args(self, parsed_args):
        # No-op by default.
        pass

    def take_action(self, parsed_args):
        self._validate_parsed_args(parsed_args)
        f = self._get_format_function()

        ret = self._get_resources(parsed_args)
        if not isinstance(ret, list):
            ret = [ret]

        data = [f(r)[1] for r in ret]

        if data:
            return f()[0], data
        return f()


@six.add_metaclass(abc.ABCMeta)
class DCManagerShowOne(command.ShowOne):
    @abc.abstractmethod
    def _get_format_function(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_resources(self, parsed_args):
        """Get a list of API resources (e.g. using client)."""
        raise NotImplementedError

    def _validate_parsed_args(self, parsed_args):
        # No-op by default.
        pass

    def take_action(self, parsed_args):
        self._validate_parsed_args(parsed_args)
        f = self._get_format_function()

        ret = self._get_resources(parsed_args)
        if not isinstance(ret, list):
            ret = [ret]

        columns = [f(r)[0] for r in ret]
        data = [f(r)[1] for r in ret]

        if data:
            return (columns[0], data[0])
        return f()


@six.add_metaclass(abc.ABCMeta)
class DCManagerShow(DCManagerLister, DCManagerShowOne):

    @abc.abstractmethod
    def should_list(self, parsed_args):
        """Uses Lister behaviour if True, ShowOne otherwise."""
        raise NotImplementedError

    def take_action(self, parsed_args):
        """Overrides method from DCManagerLister and DCManagerShowOne."""

        if self.should_list(parsed_args):
            return DCManagerLister.take_action(self, parsed_args)
        return DCManagerShowOne.take_action(self, parsed_args)

    def produce_output(self, parsed_args, column_names, data):
        """Overrides method from cliff.Lister/cliff.ShowOne."""

        if self.should_list(parsed_args):
            return DCManagerLister.produce_output(
                self, parsed_args, column_names, data
            )
        return DCManagerShowOne.produce_output(self, parsed_args, column_names, data)
