#
# Copyright (c) 2021, 2024-2026 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from dcmanagerclient.commands.v1 import sw_update_manager


class KubeRootcaUpdateManagerMixin:
    """This Mixin provides the update manager used for kube rootca updates."""

    def get_sw_update_manager(self):
        return self.app.client_manager.kube_rootca_update_manager


class CreateKubeRootcaUpdateStrategy(
    KubeRootcaUpdateManagerMixin, sw_update_manager.CreateSwUpdateStrategy
):
    """Create a kube rootca update strategy.

    This strategy supports: expiry-date, subject, algorithm and key-size
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        self.add_argument(
            "--subject",
            required=False,
            help="A subject for a generated certificate.",
        )
        self.add_argument(
            "--expiry-date",
            required=False,
            help="Expiry date for a generated certificate.",
        )
        self.add_argument(
            "--algorithm",
            required=False,
            choices=["ECDSA", "RSA"],
            help="Key algorithm of the generated root CA certificate.",
        )
        self.add_argument(
            "--key-size",
            required=False,
            type=int,
            help="Key size of the generated root CA (ECDSA 384/521, RSA 4096). "
            "Requires --algorithm.",
        )
        self.add_argument(
            "--force",
            required=False,
            action="store_true",
            help="Allow update even with in-sync endpoint status.",
        )

        return parser

    def process_custom_params(self, parsed_args, kwargs_dict):
        """Updates kwargs dictionary from parsed_args for kube rootca update"""
        if parsed_args.subject:
            kwargs_dict["subject"] = parsed_args.subject
        # Note the "-" vs "_" when dealing with parsed_args
        if parsed_args.expiry_date:
            kwargs_dict["expiry-date"] = parsed_args.expiry_date
        if parsed_args.algorithm:
            kwargs_dict["algorithm"] = parsed_args.algorithm
        if parsed_args.key_size:
            kwargs_dict["key-size"] = parsed_args.key_size
        if parsed_args.force:
            kwargs_dict["force"] = "true"


class ShowKubeRootcaUpdateStrategy(
    KubeRootcaUpdateManagerMixin, sw_update_manager.ShowSwUpdateStrategy
):
    """Show the details of a kube rootca update strategy for a subcloud."""


class DeleteKubeRootcaUpdateStrategy(
    KubeRootcaUpdateManagerMixin, sw_update_manager.DeleteSwUpdateStrategy
):
    """Delete kube rootca update strategy from the database."""


class ApplyKubeRootcaUpdateStrategy(
    KubeRootcaUpdateManagerMixin, sw_update_manager.ApplySwUpdateStrategy
):
    """Apply a kube rootca update strategy."""


class AbortKubeRootcaUpdateStrategy(
    KubeRootcaUpdateManagerMixin, sw_update_manager.AbortSwUpdateStrategy
):
    """Abort a kube rootca update strategy."""
