#
# Copyright (c) 2022 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import base64
import os

from osc_lib.command import command

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions
from dcmanagerclient import utils


def detail_format(subcloud=None):
    columns = (
        'id',
        'name',
        'description',
        'location',
        'software_version',
        'management',
        'availability',
        'deploy_status',
        'management_subnet',
        'management_start_ip',
        'management_end_ip',
        'management_gateway_ip',
        'systemcontroller_gateway_ip',
        'group_id',
        'created_at',
        'updated_at',
        'backup_status',
        'backup_datetime',
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
            subcloud.created_at,
            subcloud.updated_at,
            subcloud.backup_status,
            subcloud.backup_datetime,
        )

        for _listitem, sync_status in enumerate(subcloud.endpoint_sync_status):
            added_field = (sync_status['endpoint_type'] +
                           "_sync_status",)
            added_value = (sync_status['sync_status'],)
            columns += tuple(added_field)
            data += tuple(added_value)

        if subcloud.oam_floating_ip != "unavailable":
            columns += ('oam_floating_ip',)
            data += (subcloud.oam_floating_ip,)
    else:
        data = (tuple('<none>' for _ in range(len(columns))),)

    return columns, data


class CreateSubcloudBackup(base.DCManagerShow):
    """Backup a subcloud or group of subclouds"""

    def _get_format_function(self):
        return detail_format

    def should_list(self, parsed_args):
        return parsed_args.group

    def get_parser(self, prog_name):
        parser = super(CreateSubcloudBackup, self).get_parser(prog_name)

        parser.add_argument(
            '--local-only',
            required=False,
            action='store_true',
            help='If included, backup files will be stored on the subcloud. '
                 'Otherwise, they will be transferred and stored in '
                 'dedicated location on the system controller.'
        )

        parser.add_argument(
            '--registry-images',
            required=False,
            action='store_true',
            help='If included, container images backup file will also be '
                 'generated. This option can only be used with --local-only '
                 'option.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to create backup, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            '--backup-values',
            required=False,
            help='YAML file containing subcloud backup settings. '
                 'Can be either a local file path or a URL.'
        )

        parser.add_argument(
            '--subcloud',
            required=False,
            help='Name or ID of the subcloud to create backup.'
        )

        parser.add_argument(
            '--group',
            required=False,
            help='Name or ID of the group to create backup.'
        )

        return parser

    def _get_resources(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_backup_manager
        data = dict()
        files = dict()

        if not parsed_args.subcloud and not parsed_args.group:
            error_msg = ('Please provide the subcloud or subcloud group'
                         ' name or id.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.subcloud and parsed_args.group:
            error_msg = ('The command only applies to a single subcloud '
                         'or a subcloud group, not both.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.subcloud:
            data['subcloud'] = parsed_args.subcloud

        if parsed_args.group:
            data['group'] = parsed_args.group

        if not parsed_args.local_only and parsed_args.registry_images:
            error_msg = ('Option --registry-images can not be used without '
                         '--local-only option.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.local_only:
            data['local_only'] = 'true'
        else:
            data['local_only'] = 'false'

        if parsed_args.registry_images:
            data['registry_images'] = 'true'
        else:
            data['registry_images'] = 'false'

        if parsed_args.sysadmin_password is not None:
            # The binary base64 encoded string (eg. b'dGVzdA==') is not JSON
            # serializable in Python3.x, so it has to be decoded to a JSON
            # serializable string (eg. 'dGVzdA==').
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")).decode("utf-8")
        if parsed_args.backup_values:
            if not os.path.isfile(parsed_args.backup_values):
                error_msg = "Backup-values file does not exist: %s" % \
                            parsed_args.backup_values
                raise exceptions.DCManagerClientException(error_msg)
            files['backup_values'] = parsed_args.backup_values

        try:
            return dcmanager_client.subcloud_backup_manager.\
                backup_subcloud_create(data=data, files=files)

        except Exception as e:
            print(e)
            error_msg = "Unable to create subcloud backup"
            raise exceptions.DCManagerClientException(error_msg)


class DeleteSubcloudBackup(command.Command):
    """Delete backup from a subcloud or group of subclouds"""

    def _get_format_function(self):
        return detail_format

    def get_parser(self, prog_name):
        parser = super(DeleteSubcloudBackup, self).get_parser(prog_name)

        parser.add_argument(
            'release',
            help='Release version that the user is trying to delete.'
        )

        parser.add_argument(
            '--local-only',
            required=False,
            action='store_true',
            help='If included, backup files will be deleted from the '
                 'subcloud. Otherwise, they will be deleted from the '
                 'centralized archive on the system controller.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to delete backup, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            '--subcloud',
            required=False,
            help='Name or ID of the subcloud to delete backup.'
        )

        parser.add_argument(
            '--group',
            required=False,
            help='Name or ID of the subcloud to delete backup.'
        )

        return parser

    def take_action(self, parsed_args):
        dcmanager_client = self.app.client_manager.subcloud_backup_manager
        release_version = parsed_args.release
        subcloud_ref = parsed_args.subcloud
        data = dict()

        data['release'] = parsed_args.release

        if not parsed_args.subcloud and not parsed_args.group:
            error_msg = ('Please provide the subcloud or subcloud group'
                         ' name or id.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.subcloud and parsed_args.group:
            error_msg = ('This command only applies to a single subcloud '
                         'or a subcloud group, not both.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.subcloud:
            data['subcloud'] = parsed_args.subcloud

        if parsed_args.group:
            data['group'] = parsed_args.group

        if parsed_args.local_only:
            data['local_only'] = 'true'
        else:
            data['local_only'] = 'false'

        if parsed_args.sysadmin_password is not None:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")).decode("utf-8")
        elif not parsed_args.sysadmin_password and parsed_args.local_only:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")).decode("utf-8")

        try:
            return dcmanager_client.subcloud_backup_manager.\
                backup_subcloud_delete(subcloud_ref=subcloud_ref,
                                       release_version=release_version,
                                       data=data)

        except Exception as e:
            print(e)
            error_msg = "Unable to delete backup"
            raise exceptions.DCManagerClientException(error_msg)


class RestoreSubcloudBackup(base.DCManagerShow):
    """Restore a subcloud or group of subclouds from backup"""

    def _get_format_function(self):
        return detail_format

    def should_list(self, parsed_args):
        return parsed_args.group

    def get_parser(self, prog_name):
        parser = super(RestoreSubcloudBackup, self).get_parser(prog_name)

        parser.add_argument(
            '--with-install',
            required=False,
            action='store_true',
            help='If included, the subcloud will be reinstalled prior to '
                 'being restored from backup data.'
        )

        parser.add_argument(
            '--local-only',
            required=False,
            action='store_true',
            help='If included, the subcloud will be restored from backup data '
                 'previously saved on the subcloud. Otherwise, it will be '
                 'restored from backup data previously saved on the system '
                 'controller.'
        )

        parser.add_argument(
            '--registry-images',
            required=False,
            action='store_true',
            help='If included, user images will be restored post platform '
                 'restore. This option can only be used with --local-only '
                 'option.'

        )

        parser.add_argument(
            '--restore-values',
            required=False,
            help='Reference to the restore playbook overrides yaml file, as '
                 'listed in the product documentation for the ansible restore.'
        )

        parser.add_argument(
            '--sysadmin-password',
            required=False,
            help='sysadmin password of the subcloud to be restored, '
                 'if not provided you will be prompted.'
        )

        parser.add_argument(
            '--subcloud',
            required=False,
            help='Name or ID of the subcloud to restore.'
        )

        parser.add_argument(
            '--group',
            required=False,
            help='Name or ID of the subcloud group to restore.'
        )

        return parser

    def _get_resources(self, parsed_args):

        dcmanager_client = self.app.client_manager.subcloud_backup_manager
        data = dict()
        files = dict()

        if not parsed_args.subcloud and not parsed_args.group:
            error_msg = ('Please provide the subcloud or subcloud group'
                         ' name or id.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.subcloud and parsed_args.group:
            error_msg = ('The command only applies to a single subcloud '
                         'or a subcloud group, not both.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.subcloud:
            data['subcloud'] = parsed_args.subcloud

        if parsed_args.group:
            data['group'] = parsed_args.group

        if not parsed_args.local_only and parsed_args.registry_images:
            error_msg = ('Option --registry-images cannot be used without '
                         '--local-only option.')
            raise exceptions.DCManagerClientException(error_msg)

        if parsed_args.with_install:
            data['with_install'] = 'true'
        else:
            data['with_install'] = 'false'

        if parsed_args.local_only:
            data['local_only'] = 'true'
        else:
            data['local_only'] = 'false'

        if parsed_args.registry_images:
            data['registry_images'] = 'true'
        else:
            data['registry_images'] = 'false'

        if parsed_args.sysadmin_password is not None:
            data['sysadmin_password'] = base64.b64encode(
                parsed_args.sysadmin_password.encode("utf-8")).decode("utf-8")
        else:
            password = utils.prompt_for_password()
            data["sysadmin_password"] = base64.b64encode(
                password.encode("utf-8")).decode("utf-8")
        if parsed_args.restore_values:
            if not os.path.isfile(parsed_args.restore_values):
                error_msg = "Restore_values file does not exist: %s" % \
                            parsed_args.restore_values
                raise exceptions.DCManagerClientException(error_msg)
            files['restore_values'] = parsed_args.restore_values
        try:
            return dcmanager_client.subcloud_backup_manager.\
                backup_subcloud_restore(data=data, files=files)

        except Exception as e:
            print(e)
            error_msg = "Unable to restore subcloud backup"
            raise exceptions.DCManagerClientException(error_msg)
