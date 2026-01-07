#
# Copyright (c) 2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import base
from dcmanagerclient import exceptions


def config_format(config: dict = None) -> tuple[tuple, tuple]:
    """Format function for backup configuration display"""
    columns = (
        "Storage Location",
        "Retention Count",
        "Updated At",
    )

    if config is not None:
        updated_at = config.get("updated_at", "")

        # Convert ISO format to a more readable format
        updated_at = updated_at.replace("T", " ")
        updated_at = updated_at.split(".")[0]

        data = (
            config.get("storage_location", ""),
            str(config.get("retention_count", "")),
            updated_at,
        )
        return columns, data

    return columns, ()


class ShowSubcloudBackupConfig(base.DCManagerShowOne):
    """Show subcloud backup configuration."""

    def _get_format_function(self):
        return config_format

    def _get_resources(self, parsed_args):
        """Query the API for backup configuration"""
        config_manager = self.app.client_manager.subcloud_backup_config_manager
        return config_manager.subcloud_backup_config_show()


class UpdateSubcloudBackupConfig(base.DCManagerShowOne):
    """Update subcloud backup configuration."""

    def _get_format_function(self):
        return config_format

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            "--storage-location",
            choices=["dc-vault", "seaweedfs"],
            help="Storage location for backups: 'dc-vault' or 'seaweedfs'",
        )

        parser.add_argument(
            "--retention-count",
            type=int,
            help="Number of backups to retain per subcloud and release (1-10)",
        )

        return parser

    def _get_resources(self, parsed_args):
        """Update backup configuration via API"""
        config_manager = self.app.client_manager.subcloud_backup_config_manager

        kwargs = {}
        if parsed_args.storage_location:
            kwargs["storage_location"] = parsed_args.storage_location
        if parsed_args.retention_count is not None:
            kwargs["retention_count"] = parsed_args.retention_count

        if not kwargs:
            raise exceptions.DCManagerClientException(
                "At least one parameter (--storage-location or --retention-count) "
                "must be provided"
            )

        if parsed_args.retention_count is not None:
            if not 1 <= parsed_args.retention_count <= 10:
                raise exceptions.DCManagerClientException(
                    "retention_count must be between 1 and 10"
                )

        try:
            return config_manager.subcloud_backup_config_update(**kwargs)
        except Exception as e:
            error_msg = f"Unable to update backup configuration: {str(e)}"
            raise exceptions.DCManagerClientException(error_msg)
