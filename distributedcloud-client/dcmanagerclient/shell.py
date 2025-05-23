# Copyright 2015 - Ericsson AB.
# Copyright (c) 2017-2025 Wind River Systems, Inc.
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

"""
Command-line interface to the DC Manager APIs
"""

import argparse
import logging
import os
import sys

from cliff import app, complete
from cliff import commandmanager
from cliff import help as cliff_help
from osc_lib.command import command

from dcmanagerclient import __version__ as dcmanager_version
from dcmanagerclient import exceptions
from dcmanagerclient.api import client
from dcmanagerclient.commands.v1 import alarm_manager as am
from dcmanagerclient.commands.v1 import fw_update_manager as fum
from dcmanagerclient.commands.v1 import kube_rootca_update_manager as krum
from dcmanagerclient.commands.v1 import kube_upgrade_manager as kupm
from dcmanagerclient.commands.v1 import peer_group_association_manager as pgam
from dcmanagerclient.commands.v1 import phased_subcloud_deploy_manager as psdm
from dcmanagerclient.commands.v1 import subcloud_backup_manager as sbm
from dcmanagerclient.commands.v1 import subcloud_deploy_manager as sdm
from dcmanagerclient.commands.v1 import subcloud_group_manager as gm
from dcmanagerclient.commands.v1 import subcloud_manager as sm
from dcmanagerclient.commands.v1 import subcloud_peer_group_manager as pm
from dcmanagerclient.commands.v1 import sw_deploy_manager as swdm
from dcmanagerclient.commands.v1 import sw_prestage_manager as spr
from dcmanagerclient.commands.v1 import sw_update_manager as swum
from dcmanagerclient.commands.v1 import sw_update_options_manager as suom
from dcmanagerclient.commands.v1 import system_peer_manager as sp


def env(*args, **kwargs):
    """Returns the first environment variable set.

    If all are empty, defaults to '' or keyword arg `default`.
    """
    for arg in args:
        value = os.environ.get(arg)
        if value:
            return value
    return kwargs.get("default", "")


class OpenStackHelpFormatter(argparse.HelpFormatter):
    def __init__(
        self,
        prog,
        indent_increment=2,
        max_help_position=32,
        width=None,
    ):
        super().__init__(prog, indent_increment, max_help_position, width)

    def start_section(self, heading):
        # Title-case the headings.
        heading = f"{heading[0].upper()}{heading[1:]}"
        super().start_section(heading)


class HelpCommand(cliff_help.HelpCommand):
    """print detailed help for another command

    Provide a custom action so the help command without
    arguments could use our custom HelpAction

    """

    def take_action(self, parsed_args):
        if parsed_args.cmd:
            super().take_action(parsed_args)
        else:
            action = HelpAction(None, None, default=self.app)
            action(self.app.parser, self.app.options, None, None)
        return 0


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
        main_app = self.default
        parser.print_help(main_app.stdout)
        main_app.stdout.write("\nCommands for API v1 :\n")

        for name, app_cmd in sorted(main_app.command_manager):
            factory = app_cmd.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split("\n")[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)

        for name, one_liner in outputs:
            main_app.stdout.write(f"  {name.ljust(max_len)}  {one_liner}\n")

        sys.exit(0)


class BashCompletionCommand(command.Command):
    """Prints all of the commands and options for bash-completion."""

    def take_action(self, parsed_args):
        commands = set()
        options = set()

        for (
            option,
            _,
        ) in self.app.parser._option_string_actions.items():
            options.add(option)

        for command_name, _ in self.app.command_manager:
            commands.add(command_name)

        print(" ".join(commands | options))


class CustomBashCompletion(complete.CompleteBash):
    """Overrides the default bash completion command
    to use a custom bash completion where dash is
    replaced by two underscores instead of one

    """

    def write(self, cmdo, data):
        self.output.write(self.get_header())
        self.output.write(f"cmds='{cmdo}'\n")
        for datum in data:
            datum = (datum[0].replace("-", "__"), datum[1])
            self.output.write(f"cmds_{datum[0]}='{datum[1]}'\n")
        self.output.write(self.get_trailer())

    @property
    def escaped_name(self):
        return self.name.replace("-", "__")

    def get_trailer(self):
        return (
            """
  dash=-
  underscore=__
  cmd=""
  words[0]=""
  completed="${cmds}"
  for var in "${words[@]:1}"
  do
    if [[ ${var} == -* ]] ; then
      break
    fi
    if [ -z "${cmd}" ] ; then
      proposed="${var}"
    else
      proposed="${cmd}_${var}"
    fi
    local i="cmds_${proposed}"
    i=${i//$dash/$underscore}
    local comp="${!i}"
    if [ -z "${comp}" ] ; then
      break
    fi
    if [[ ${comp} == -* ]] ; then
      if [[ ${cur} != -* ]] ; then
        completed=""
        break
      fi
    fi
    cmd="${proposed}"
    completed="${comp}"
  done

  if [ -z "${completed}" ] ; then
    COMPREPLY=( $( compgen -f -- "$cur" ) $( compgen -d -- "$cur" ) )
  else
    COMPREPLY=( $(compgen -W "${completed}" -- ${cur}) )
  fi
  return 0
}
complete -F _"""
            + self.escaped_name
            + " "
            + self.name
            + "\n"
        )


class CustomCompleteCommand(complete.CompleteCommand):
    """Custom completion command.

    Provides a custom bash completion command so the dash
    separator becomes two underscores instead of one to
    better distinguish a space from a dash.

    """

    def take_action(self, parsed_args):
        name = parsed_args.name or self.app.NAME
        shell = CustomBashCompletion(name, self.app.stdout)
        dicto = complete.CompleteDictionary()
        for cmd in self.app.command_manager:
            _command = cmd[0].split()
            dicto.add_command(_command, self.get_actions(_command))
        shell.write(dicto.get_commands(), dicto.get_data())
        return 0


class DCManagerShell(app.App):
    def __init__(self):
        super().__init__(
            description=__doc__.strip(),
            version=dcmanager_version,
            command_manager=commandmanager.CommandManager("dcmanager.cli"),
            deferred_help=True,
        )

        # Override default help command
        self.command_manager.add_command("help", HelpCommand)

        # Override default completion command
        self.command_manager.add_command("complete", CustomCompleteCommand)

        # Set v1 commands by default
        self._set_shell_commands(self._get_commands(version=1))

        self.client = None
        self.client_manager = None

    def configure_logging(self):
        log_lvl = logging.DEBUG if self.options.debug else logging.WARNING
        logging.basicConfig(
            format="%(levelname)s (%(module)s) %(message)s",
            level=log_lvl,
        )
        logging.getLogger("iso8601").setLevel(logging.WARNING)

        if self.options.verbose_level <= 1:
            logging.getLogger("requests").setLevel(logging.WARNING)

    def build_option_parser(self, description, version, argparse_kwargs=None):
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
            **argparse_kwargs,
        )

        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {version}",
            help="Show program's version number and exit.",
        )

        parser.add_argument(
            "-v",
            "--verbose",
            action="count",
            dest="verbose_level",
            default=self.DEFAULT_VERBOSE_LEVEL,
            help="Increase verbosity of output. Can be repeated.",
        )

        parser.add_argument(
            "--log-file",
            action="store",
            default=None,
            help="Specify a file to log output. Disabled by default.",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            action="store_const",
            dest="verbose_level",
            const=0,
            help="Suppress output except warnings and errors.",
        )

        if self.deferred_help:
            parser.add_argument(
                "-h",
                "--help",
                dest="deferred_help",
                action="store_true",
                help="Show help message and exit.",
            )
        else:
            parser.add_argument(
                "-h",
                "--help",
                action=HelpAction,
                nargs=0,
                default=self,  # tricky
                help="Show help message and exit.",
            )

        parser.add_argument(
            "--debug",
            default=False,
            action="store_true",
            help="Show tracebacks on errors.",
        )

        parser.add_argument(
            "--dcmanager-url",
            action="store",
            dest="dcmanager_url",
            default=env("DCMANAGER_URL"),
            help="DC Manager API host (Env: DCMANAGER_URL)",
        )

        parser.add_argument(
            "--dcmanager-api-version",
            action="store",
            dest="dcmanager_version",
            default=env("DCMANAGER_API_VERSION", default="v1.0"),
            help="DC Manager API version (default = v1.0) (Env: "
            "DCMANAGER_API_VERSION)",
        )

        parser.add_argument(
            "--dcmanager-service-type",
            action="store",
            dest="service_type",
            default=env("DCMANAGER_SERVICE_TYPE", default="dcmanager"),
            help="DC Manager service-type (should be the same name as in "
            "keystone-endpoint) (default = dcmanager) (Env: "
            "DCMANAGER_SERVICE_TYPE)",
        )

        parser.add_argument(
            "--os-endpoint-type",
            action="store",
            dest="endpoint_type",
            default=env("OS_ENDPOINT_TYPE", default="internalURL"),
            help="DC Manager endpoint-type (should be the same name as in "
            "keystone-endpoint) (default = OS_ENDPOINT_TYPE)",
        )

        parser.add_argument(
            "--os-username",
            action="store",
            dest="username",
            default=env("OS_USERNAME", default="admin"),
            help="Authentication username (Env: OS_USERNAME)",
        )

        parser.add_argument(
            "--os-password",
            action="store",
            dest="password",
            default=env("OS_PASSWORD"),
            help="Authentication password (Env: OS_PASSWORD)",
        )

        parser.add_argument(
            "--os-tenant-id",
            action="store",
            dest="tenant_id",
            default=env("OS_TENANT_ID", "OS_PROJECT_ID"),
            help="Authentication tenant identifier (Env: OS_TENANT_ID)",
        )

        parser.add_argument(
            "--os-project-id",
            action="store",
            dest="project_id",
            default=env("OS_TENANT_ID", "OS_PROJECT_ID"),
            help="Authentication project identifier (Env: OS_TENANT_ID"
            " or OS_PROJECT_ID), will use tenant_id if both tenant_id"
            " and project_id are set",
        )

        parser.add_argument(
            "--os-tenant-name",
            action="store",
            dest="tenant_name",
            default=env("OS_TENANT_NAME", "OS_PROJECT_NAME"),
            help="Authentication tenant name (Env: OS_TENANT_NAME)",
        )

        parser.add_argument(
            "--os-project-name",
            action="store",
            dest="project_name",
            default=env("OS_TENANT_NAME", "OS_PROJECT_NAME"),
            help="Authentication project name (Env: OS_TENANT_NAME"
            " or OS_PROJECT_NAME), will use tenant_name if both"
            " tenant_name and project_name are set",
        )

        parser.add_argument(
            "--os-auth-token",
            action="store",
            dest="token",
            default=env("OS_AUTH_TOKEN"),
            help="Authentication token (Env: OS_AUTH_TOKEN)",
        )

        parser.add_argument(
            "--os-project-domain-name",
            action="store",
            dest="project_domain_name",
            default=env("OS_PROJECT_DOMAIN_NAME"),
            help="Authentication project domain name or ID"
            " (Env: OS_PROJECT_DOMAIN_NAME)",
        )

        parser.add_argument(
            "--os-project-domain-id",
            action="store",
            dest="project_domain_id",
            default=env("OS_PROJECT_DOMAIN_ID"),
            help="Authentication project domain ID" " (Env: OS_PROJECT_DOMAIN_ID)",
        )

        parser.add_argument(
            "--os-user-domain-name",
            action="store",
            dest="user_domain_name",
            default=env("OS_USER_DOMAIN_NAME"),
            help="Authentication user domain name" " (Env: OS_USER_DOMAIN_NAME)",
        )

        parser.add_argument(
            "--os-user-domain-id",
            action="store",
            dest="user_domain_id",
            default=env("OS_USER_DOMAIN_ID"),
            help="Authentication user domain name" " (Env: OS_USER_DOMAIN_ID)",
        )

        parser.add_argument(
            "--os-auth-url",
            action="store",
            dest="auth_url",
            default=env("OS_AUTH_URL"),
            help="Authentication URL (Env: OS_AUTH_URL)",
        )

        parser.add_argument(
            "--os-cacert",
            action="store",
            dest="cacert",
            default=env("OS_CACERT"),
            help="Authentication CA Certificate (Env: OS_CACERT)",
        )

        parser.add_argument(
            "--insecure",
            action="store_true",
            dest="insecure",
            default=env("DCMANAGERCLIENT_INSECURE", default=False),
            help="Disables SSL/TLS certificate verification "
            "(Env: DCMANAGERCLIENT_INSECURE)",
        )

        parser.add_argument(
            "--profile",
            dest="profile",
            metavar="HMAC_KEY",
            help=(
                "HMAC key to use for encrypting context data for performance "
                "profiling of operation. This key should be one of the "
                "values configured for the osprofiler middleware in "
                "dcmanager, it is specified in the profiler section of the "
                "dcmanager configuration (i.e. /etc/dcmanager/dcmanager.conf). "
                "Without the key, profiling will not be triggered even if "
                "osprofiler is enabled on the server side."
            ),
        )

        return parser

    def print_help_if_requested(self):
        if self.deferred_help and self.options.deferred_help:
            action = HelpAction(None, None, default=self)
            action(self.parser, self.options, None, None)

    def initialize_app(self, argv):
        self._clear_shell_commands()

        ver = client.determine_client_version(self.options.dcmanager_version)

        self._set_shell_commands(self._get_commands(ver))

        no_auth_commands = {"help", "bash-completion", "complete"}

        # Skip authentication if the first argument is a no-auth command or
        # if deferred_help is True
        skip_auth = (
            argv[0] in no_auth_commands if argv else False
        ) or self.options.deferred_help

        if skip_auth:
            self.options.auth_url = None

        if self.options.auth_url and not self.options.token and not skip_auth:
            if not self.options.tenant_name:
                raise exceptions.CommandError(
                    (
                        "You must provide a tenant_name "
                        "via --os-tenantname env[OS_TENANT_NAME]"
                    )
                )
            if not self.options.username:
                raise exceptions.CommandError(
                    (
                        "You must provide a username "
                        "via --os-username env[OS_USERNAME]"
                    )
                )

            if not self.options.password:
                raise exceptions.CommandError(
                    (
                        "You must provide a password "
                        "via --os-password env[OS_PASSWORD]"
                    )
                )

        kwargs = {
            "user_domain_name": self.options.user_domain_name,
            "user_domain_id": self.options.user_domain_id,
            "project_domain_name": self.options.project_domain_name,
            "project_domain_id": self.options.project_domain_id,
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
            **kwargs,
        )

        if not self.options.auth_url and not skip_auth:
            raise exceptions.CommandError(
                (
                    "You must provide an auth url via either "
                    "--os-auth-url or env[OS_AUTH_URL] or "
                    "specify an auth_system which defines a"
                    " default url with --os-auth-system or env[OS_AUTH_SYSTEM]"
                )
            )

        phased_subcloud_deploy_manager = self.client.phased_subcloud_deploy_manager
        peer_group_association_manager = self.client.peer_group_association_manager
        client_keys = {
            "alarm_manager": self.client.alarm_manager,
            "fw_update_manager": self.client.fw_update_manager,
            "kube_rootca_update_manager": self.client.kube_rootca_update_manager,
            "kube_upgrade_manager": self.client.kube_upgrade_manager,
            "peer_group_association_manager": peer_group_association_manager,
            "phased_subcloud_deploy_manager": phased_subcloud_deploy_manager,
            "strategy_step_manager": self.client.strategy_step_manager,
            "subcloud_backup_manager": self.client.subcloud_backup_manager,
            "subcloud_deploy_manager": self.client.subcloud_deploy_manager,
            "subcloud_group_manager": self.client.subcloud_group_manager,
            "subcloud_peer_group_manager": self.client.subcloud_peer_group_manager,
            "subcloud_manager": self.client.subcloud_manager,
            "sw_deploy_manager": self.client.sw_deploy_manager,
            "sw_prestage_manager": self.client.sw_prestage_manager,
            "sw_update_options_manager": self.client.sw_update_options_manager,
            "system_peer_manager": self.client.system_peer_manager,
        }

        # Adding client_manager variable to make dcmanager client work with
        # unified OpenStack client.
        ClientManager = type(
            "ClientManager",
            (object,),
            client_keys,
        )
        self.client_manager = ClientManager()

    def _set_shell_commands(self, cmds_dict):
        for cmd, cmd_class in cmds_dict.items():
            self.command_manager.add_command(cmd, cmd_class)

    def _clear_shell_commands(self):
        exclude_cmds = ["help", "complete"]

        cmds = self.command_manager.commands.copy()
        for k, _ in cmds.items():
            if k not in exclude_cmds:
                self.command_manager.commands.pop(k)

    def _get_commands(self, version):
        if version == 1:
            return self._get_commands_v1()
        return {}

    @staticmethod
    def _get_commands_v1():
        list_system_peer_groups = sp.ListSystemPeerSubcloudPeerGroups
        create_kube_root_update = krum.CreateKubeRootcaUpdateStrategy
        delete_kube_root_update = krum.DeleteKubeRootcaUpdateStrategy
        return {
            "alarm summary": am.ListAlarmSummary,
            "bash-completion": BashCompletionCommand,
            "fw-update-strategy abort": fum.AbortFwUpdateStrategy,
            "fw-update-strategy apply": fum.ApplyFwUpdateStrategy,
            "fw-update-strategy create": fum.CreateFwUpdateStrategy,
            "fw-update-strategy delete": fum.DeleteFwUpdateStrategy,
            "fw-update-strategy show": fum.ShowFwUpdateStrategy,
            "kube-rootca-update-strategy abort": krum.AbortKubeRootcaUpdateStrategy,
            "kube-rootca-update-strategy apply": krum.ApplyKubeRootcaUpdateStrategy,
            "kube-rootca-update-strategy create": create_kube_root_update,
            "kube-rootca-update-strategy delete": delete_kube_root_update,
            "kube-rootca-update-strategy show": krum.ShowKubeRootcaUpdateStrategy,
            "kube-upgrade-strategy abort": kupm.AbortKubeUpgradeStrategy,
            "kube-upgrade-strategy apply": kupm.ApplyKubeUpgradeStrategy,
            "kube-upgrade-strategy create": kupm.CreateKubeUpgradeStrategy,
            "kube-upgrade-strategy delete": kupm.DeleteKubeUpgradeStrategy,
            "kube-upgrade-strategy show": kupm.ShowKubeUpgradeStrategy,
            "peer-group-association add": pgam.AddPeerGroupAssociation,
            "peer-group-association delete": pgam.DeletePeerGroupAssociation,
            "peer-group-association list": pgam.ListPeerGroupAssociation,
            "peer-group-association show": pgam.ShowPeerGroupAssociation,
            "peer-group-association sync": pgam.SyncPeerGroupAssociation,
            "peer-group-association update": pgam.UpdatePeerGroupAssociation,
            "prestage-strategy abort": spr.AbortSwPrestageStrategy,
            "prestage-strategy apply": spr.ApplySwPrestageStrategy,
            "prestage-strategy create": spr.CreateSwPrestageStrategy,
            "prestage-strategy delete": spr.DeleteSwPrestageStrategy,
            "prestage-strategy show": spr.ShowSwPrestageStrategy,
            "strategy-step list": swum.ListSwUpdateStrategyStep,
            "strategy-step show": swum.ShowSwUpdateStrategyStep,
            "strategy-config delete": suom.DeleteSwUpdateOptions,
            "strategy-config list": suom.ListSwUpdateOptions,
            "strategy-config show": suom.ShowSwUpdateOptions,
            "strategy-config update": suom.UpdateSwUpdateOptions,
            "subcloud add": sm.AddSubcloud,
            "subcloud delete": sm.DeleteSubcloud,
            "subcloud deploy abort": psdm.AbortPhasedSubcloudDeploy,
            "subcloud deploy bootstrap": psdm.BootstrapPhasedSubcloudDeploy,
            "subcloud deploy complete": psdm.CompletePhasedSubcloudDeploy,
            "subcloud deploy config": psdm.ConfigPhasedSubcloudDeploy,
            "subcloud deploy create": psdm.CreatePhasedSubcloudDeploy,
            "subcloud deploy delete": sdm.SubcloudDeployDelete,
            "subcloud deploy install": psdm.InstallPhasedSubcloudDeploy,
            "subcloud deploy resume": psdm.PhasedSubcloudDeployResume,
            "subcloud deploy enroll": psdm.EnrollPhasedSubcloudDeploy,
            "subcloud deploy show": sdm.SubcloudDeployShow,
            "subcloud deploy upload": sdm.SubcloudDeployUpload,
            "subcloud errors": sm.ShowSubcloudError,
            "subcloud list": sm.ListSubcloud,
            "subcloud manage": sm.ManageSubcloud,
            "subcloud reconfig": sm.ReconfigSubcloud,
            "subcloud redeploy": sm.RedeploySubcloud,
            "subcloud reinstall": sm.ReinstallSubcloud,
            "subcloud restore": sm.RestoreSubcloud,
            "subcloud show": sm.ShowSubcloud,
            "subcloud prestage": sm.PrestageSubcloud,
            "subcloud unmanage": sm.UnmanageSubcloud,
            "subcloud update": sm.UpdateSubcloud,
            "subcloud-backup create": sbm.CreateSubcloudBackup,
            "subcloud-backup delete": sbm.DeleteSubcloudBackup,
            "subcloud-backup restore": sbm.RestoreSubcloudBackup,
            "subcloud-deploy show": sdm.DeprecatedSubcloudDeployShow,
            "subcloud-deploy upload": sdm.DeprecatedSubcloudDeployUpload,
            "subcloud-group add": gm.AddSubcloudGroup,
            "subcloud-group delete": gm.DeleteSubcloudGroup,
            "subcloud-group list": gm.ListSubcloudGroup,
            "subcloud-group list-subclouds": gm.ListSubcloudGroupSubclouds,
            "subcloud-group show": gm.ShowSubcloudGroup,
            "subcloud-group update": gm.UpdateSubcloudGroup,
            "subcloud-peer-group add": pm.AddSubcloudPeerGroup,
            "subcloud-peer-group delete": pm.DeleteSubcloudPeerGroup,
            "subcloud-peer-group list": pm.ListSubcloudPeerGroup,
            "subcloud-peer-group list-subclouds": pm.ListSubcloudPeerGroupSubclouds,
            "subcloud-peer-group migrate": pm.MigrateSubcloudPeerGroup,
            "subcloud-peer-group show": pm.ShowSubcloudPeerGroup,
            "subcloud-peer-group status": pm.StatusSubcloudPeerGroup,
            "subcloud-peer-group update": pm.UpdateSubcloudPeerGroup,
            "sw-deploy-strategy abort": swdm.AbortSwDeployStrategy,
            "sw-deploy-strategy apply": swdm.ApplySwDeployStrategy,
            "sw-deploy-strategy create": swdm.CreateSwDeployStrategy,
            "sw-deploy-strategy delete": swdm.DeleteSwDeployStrategy,
            "sw-deploy-strategy show": swdm.ShowSwDeployStrategy,
            "system-peer add": sp.AddSystemPeer,
            "system-peer delete": sp.DeleteSystemPeer,
            "system-peer list": sp.ListSystemPeer,
            "system-peer list-subcloud-peer-groups": list_system_peer_groups,
            "system-peer show": sp.ShowSystemPeer,
            "system-peer update": sp.UpdateSystemPeer,
        }


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    return DCManagerShell().run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
