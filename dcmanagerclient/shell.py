# Copyright 2015 - Ericsson AB.
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

"""
Command-line interface to the DC Manager APIs
"""

import logging
import sys

from dcmanagerclient import __version__ as dcmanager_version
from dcmanagerclient.api import client
from dcmanagerclient import exceptions
from dcmanagerclient.openstack.common import cliutils as c

from cliff import app
from cliff import commandmanager
from osc_lib.command import command

import argparse
from dcmanagerclient.commands.v1 import alarm_manager as am
from dcmanagerclient.commands.v1 import subcloud_manager as sm
from dcmanagerclient.commands.v1 import sw_update_manager as sum
from dcmanagerclient.commands.v1 import sw_update_options_manager as suom

LOG = logging.getLogger(__name__)


class OpenStackHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=32,
                 width=None):
        super(OpenStackHelpFormatter, self).__init__(
            prog,
            indent_increment,
            max_help_position,
            width
        )

    def start_section(self, heading):
        # Title-case the headings.
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


class HelpAction(argparse.Action):
    """Custom help action.

    Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v1 :\n')

        for name, ep in sorted(app.command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)

        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))

        sys.exit(0)


class BashCompletionCommand(command.Command):
    """Prints all of the commands and options for bash-completion."""

    def take_action(self, parsed_args):
        commands = set()
        options = set()

        for option, _action in self.app.parser._option_string_actions.items():
            options.add(option)

        for command_name, _cmd in self.app.command_manager:
            commands.add(command_name)

        print(' '.join(commands | options))


class DCManagerShell(app.App):
    def __init__(self):
        super(DCManagerShell, self).__init__(
            description=__doc__.strip(),
            version=dcmanager_version,
            command_manager=commandmanager.CommandManager('dcmanager.cli'),
        )

        # Set v1 commands by default
        self._set_shell_commands(self._get_commands(version=1))

    def configure_logging(self):
        log_lvl = logging.DEBUG if self.options.debug else logging.WARNING
        logging.basicConfig(
            format="%(levelname)s (%(module)s) %(message)s",
            level=log_lvl
        )
        logging.getLogger('iso8601').setLevel(logging.WARNING)

        if self.options.verbose_level <= 1:
            logging.getLogger('requests').setLevel(logging.WARNING)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}

        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
            **argparse_kwargs
        )

        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            help='Show program\'s version number and exit.'
        )

        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )

        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )

        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )

        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="Show this help message and exit.",
        )

        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )

        parser.add_argument(
            '--dcmanager-url',
            action='store',
            dest='dcmanager_url',
            default=c.env('DCMANAGER_URL'),
            help='DC Manager API host (Env: DCMANAGER_URL)'
        )

        parser.add_argument(
            '--dcmanager-api-version',
            action='store',
            dest='dcmanager_version',
            default=c.env('DCMANAGER_API_VERSION', default='v1.0'),
            help='DC Manager API version (default = v1.0) (Env: '
                 'DCMANAGER_API_VERSION)'
        )

        parser.add_argument(
            '--dcmanager-service-type',
            action='store',
            dest='service_type',
            default=c.env('DCMANAGER_SERVICE_TYPE',
                          default='dcmanager'),
            help='DC Manager service-type (should be the same name as in '
                 'keystone-endpoint) (default = dcmanager) (Env: '
                 'DCMANAGER_SERVICE_TYPE)'
        )

        parser.add_argument(
            '--os-endpoint-type',
            action='store',
            dest='endpoint_type',
            default=c.env('OS_ENDPOINT_TYPE',
                          default='internalURL'),
            help='DC Manager endpoint-type (should be the same name as in '
                 'keystone-endpoint) (default = OS_ENDPOINT_TYPE)'
        )

        parser.add_argument(
            '--os-username',
            action='store',
            dest='username',
            default=c.env('OS_USERNAME', default='admin'),
            help='Authentication username (Env: OS_USERNAME)'
        )

        parser.add_argument(
            '--os-password',
            action='store',
            dest='password',
            default=c.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)'
        )

        parser.add_argument(
            '--os-tenant-id',
            action='store',
            dest='tenant_id',
            default=c.env('OS_TENANT_ID', 'OS_PROJECT_ID'),
            help='Authentication tenant identifier (Env: OS_TENANT_ID)'
        )

        parser.add_argument(
            '--os-project-id',
            action='store',
            dest='project_id',
            default=c.env('OS_TENANT_ID', 'OS_PROJECT_ID'),
            help='Authentication project identifier (Env: OS_TENANT_ID'
                 ' or OS_PROJECT_ID), will use tenant_id if both tenant_id'
                 ' and project_id are set'
        )

        parser.add_argument(
            '--os-tenant-name',
            action='store',
            dest='tenant_name',
            default=c.env('OS_TENANT_NAME', 'OS_PROJECT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)'
        )

        parser.add_argument(
            '--os-project-name',
            action='store',
            dest='project_name',
            default=c.env('OS_TENANT_NAME', 'OS_PROJECT_NAME'),
            help='Authentication project name (Env: OS_TENANT_NAME'
                 ' or OS_PROJECT_NAME), will use tenant_name if both'
                 ' tenant_name and project_name are set'
        )

        parser.add_argument(
            '--os-auth-token',
            action='store',
            dest='token',
            default=c.env('OS_AUTH_TOKEN'),
            help='Authentication token (Env: OS_AUTH_TOKEN)'
        )

        parser.add_argument(
            '--os-project-domain-name',
            action='store',
            dest='project_domain_name',
            default=c.env('OS_PROJECT_DOMAIN_NAME'),
            help='Authentication project domain name or ID'
                 ' (Env: OS_PROJECT_DOMAIN_NAME)'
        )

        parser.add_argument(
            '--os-project-domain-id',
            action='store',
            dest='project_domain_id',
            default=c.env('OS_PROJECT_DOMAIN_ID'),
            help='Authentication project domain ID'
                 ' (Env: OS_PROJECT_DOMAIN_ID)'
        )

        parser.add_argument(
            '--os-user-domain-name',
            action='store',
            dest='user_domain_name',
            default=c.env('OS_USER_DOMAIN_NAME'),
            help='Authentication user domain name'
                 ' (Env: OS_USER_DOMAIN_NAME)'
        )

        parser.add_argument(
            '--os-user-domain-id',
            action='store',
            dest='user_domain_id',
            default=c.env('OS_USER_DOMAIN_ID'),
            help='Authentication user domain name'
                 ' (Env: OS_USER_DOMAIN_ID)'
        )

        parser.add_argument(
            '--os-auth-url',
            action='store',
            dest='auth_url',
            default=c.env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)'
        )

        parser.add_argument(
            '--os-cacert',
            action='store',
            dest='cacert',
            default=c.env('OS_CACERT'),
            help='Authentication CA Certificate (Env: OS_CACERT)'
        )

        parser.add_argument(
            '--insecure',
            action='store_true',
            dest='insecure',
            default=c.env('DCMANAGERCLIENT_INSECURE', default=False),
            help='Disables SSL/TLS certificate verification '
                 '(Env: DCMANAGERCLIENT_INSECURE)'
        )

        parser.add_argument(
            '--profile',
            dest='profile',
            metavar='HMAC_KEY',
            help='HMAC key to use for encrypting context data for performance '
                 'profiling of operation. This key should be one of the '
                 'values configured for the osprofiler middleware in '
                 'dcmanager, it is specified in the profiler section of the '
                 'dcmanager configuration '
                 '(i.e. /etc/dcmanager/dcmanager.conf). '
                 'Without the key, profiling will not be triggered even if '
                 'osprofiler is enabled on the server side.'
        )

        return parser

    def initialize_app(self, argv):
        self._clear_shell_commands()

        ver = client.determine_client_version(self.options.dcmanager_version)

        self._set_shell_commands(self._get_commands(ver))

        do_help = ['help', '-h', 'bash-completion', 'complete']

        # bash-completion should not require authentication.
        skip_auth = ''.join(argv) in do_help

        if skip_auth:
            self.options.auth_url = None

        if self.options.auth_url and not self.options.token \
            and not skip_auth:
            if not self.options.tenant_name:
                raise exceptions.CommandError(
                    ("You must provide a tenant_name "
                     "via --os-tenantname env[OS_TENANT_NAME]")
                )
            if not self.options.username:
                raise exceptions.CommandError(
                    ("You must provide a username "
                     "via --os-username env[OS_USERNAME]")
                )

            if not self.options.password:
                raise exceptions.CommandError(
                    ("You must provide a password "
                     "via --os-password env[OS_PASSWORD]")
                )

        kwargs = {
            'user_domain_name': self.options.user_domain_name,
            'user_domain_id': self.options.user_domain_id,
            'project_domain_name': self.options.project_domain_name,
            'project_domain_id': self.options.project_domain_id
        }

        self.client = client.client(
            dcmanager_url=self.options.dcmanager_url,
            username=self.options.username,
            api_key=self.options.password,
            project_name=self.options.tenant_name or self.options.project_name,
            auth_url=self.options.auth_url,
            project_id=self.options.tenant_id,
            endpoint_type=self.options.endpoint_type,
            service_type=self.options.service_type,
            auth_token=self.options.token,
            cacert=self.options.cacert,
            insecure=self.options.insecure,
            profile=self.options.profile,
            **kwargs
        )

        if not self.options.auth_url and not skip_auth:
            raise exceptions.CommandError(
                ("You must provide an auth url via either "
                 "--os-auth-url or env[OS_AUTH_URL] or "
                 "specify an auth_system which defines a"
                 " default url with --os-auth-system or env[OS_AUTH_SYSTEM]")
                )

        # Adding client_manager variable to make dcmanager client work with
        # unified OpenStack client.
        ClientManager = type(
            'ClientManager',
            (object,),
            dict(subcloud_manager=self.client,
                 alarm_manager=self.client,
                 sw_update_manager=self.client,
                 strategy_step_manager=self.client,
                 sw_update_options_manager=self.client)
        )
        self.client_manager = ClientManager()

    def _set_shell_commands(self, cmds_dict):
        for k, v in cmds_dict.items():
            self.command_manager.add_command(k, v)

    def _clear_shell_commands(self):
        exclude_cmds = ['help', 'complete']

        cmds = self.command_manager.commands.copy()
        for k, v in cmds.items():
            if k not in exclude_cmds:
                self.command_manager.commands.pop(k)

    def _get_commands(self, version):
        if version == 1:
            return self._get_commands_v1()

        return {}

    @staticmethod
    def _get_commands_v1():
        return {
            'bash-completion': BashCompletionCommand,
            'subcloud add': sm.AddSubcloud,
            'subcloud delete': sm.DeleteSubcloud,
            'subcloud list': sm.ListSubcloud,
            'subcloud show': sm.ShowSubcloud,
            'subcloud unmanage': sm.UnmanageSubcloud,
            'subcloud manage': sm.ManageSubcloud,
            'subcloud update': sm.UpdateSubcloud,
            'subcloud generate-config': sm.GenerateConfigSubcloud,
            'alarm summary': am.ListAlarmSummary,
            'patch-strategy create': sum.CreatePatchStrategy,
            'patch-strategy delete': sum.DeletePatchStrategy,
            'patch-strategy apply': sum.ApplyPatchStrategy,
            'patch-strategy abort': sum.AbortPatchStrategy,
            'patch-strategy show': sum.ShowPatchStrategy,
            'strategy-step list': sum.ListStrategyStep,
            'strategy-step show': sum.ShowStrategyStep,
            'patch-strategy-config update': suom.UpdateSwUpdateOptions,
            'patch-strategy-config list': suom.ListSwUpdateOptions,
            'patch-strategy-config show': suom.ShowSwUpdateOptions,
            'patch-strategy-config delete': suom.DeleteSwUpdateOptions,
        }


def main(argv=sys.argv[1:]):
    return DCManagerShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
