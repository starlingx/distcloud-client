#
# Copyright (c) 2020-2021 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

import mock

from oslo_utils import timeutils

from dcmanagerclient.api.v1.sw_update_manager import SwUpdateStrategy

TIME_NOW = timeutils.utcnow().isoformat()
DEFAULT_APPLY_TYPE = 'serial'
DEFAULT_MAX_PARALLEL = 2
DEFAULT_STATE = 'initial'
DEFAULT_STRATEGY_TYPE = 'patch'


def make_strategy(manager=None,
                  strategy_type=DEFAULT_STRATEGY_TYPE,
                  subcloud_apply_type=DEFAULT_APPLY_TYPE,
                  max_parallel_subclouds=DEFAULT_MAX_PARALLEL,
                  stop_on_failure=False,
                  state=DEFAULT_STATE,
                  created_at=TIME_NOW,
                  updated_at=None):
    if manager is None:
        manager = mock.MagicMock()
    return SwUpdateStrategy(manager,
                            strategy_type,
                            subcloud_apply_type,
                            max_parallel_subclouds,
                            stop_on_failure,
                            state,
                            created_at,
                            updated_at)
