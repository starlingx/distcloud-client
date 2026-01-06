# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
# Copyright 2016 - Ericsson AB.
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

import datetime
import logging
from typing import Union

import keystoneauth1.identity.generic as auth_plugin
import osprofiler.profiler
from keystoneauth1 import session as ks_session

from dcmanagerclient import utils
from dcmanagerclient.api import httpclient
from dcmanagerclient.api.v1.alarm_manager import AlarmManager
from dcmanagerclient.api.v1.fw_update_manager import FwUpdateManager
from dcmanagerclient.api.v1.kube_rootca_update_manager import KubeRootcaUpdateManager
from dcmanagerclient.api.v1.kube_upgrade_manager import KubeUpgradeManager
from dcmanagerclient.api.v1.peer_group_association_manager import (
    PeerGroupAssociationManager,
)
from dcmanagerclient.api.v1.phased_subcloud_deploy_manager import (
    PhasedSubcloudDeployManager,
)
from dcmanagerclient.api.v1.strategy_step_manager import StrategyStepManager
from dcmanagerclient.api.v1.subcloud_backup_manager import SubcloudBackupManager
from dcmanagerclient.api.v1.subcloud_deploy_manager import SubcloudDeployManager
from dcmanagerclient.api.v1.subcloud_group_manager import SubcloudGroupManager
from dcmanagerclient.api.v1.subcloud_manager import SubcloudManager
from dcmanagerclient.api.v1.subcloud_peer_group_manager import SubcloudPeerGroupManager
from dcmanagerclient.api.v1.sw_deploy_manager import SwDeployManager
from dcmanagerclient.api.v1.sw_prestage_manager import SwPrestageManager
from dcmanagerclient.api.v1.sw_strategy_manager import SwStrategyManager
from dcmanagerclient.api.v1.sw_update_options_manager import SwUpdateOptionsManager
from dcmanagerclient.api.v1.system_peer_manager import SystemPeerManager

LOG = logging.getLogger(__name__)
_DEFAULT_DCMANAGER_URL = "http://localhost:8119/v1.0"


def _cache_key(username: Union[str, None] = None) -> str:
    if username:
        return f"dcmanager_client:session:{username}"
    return "dcmanager_client:session"


class Client:
    """Class where the communication from KB to Keystone happens."""

    def __init__(
        self,
        dcmanager_url=None,
        username=None,
        api_key=None,
        project_name=None,
        auth_url=None,
        project_id=None,
        endpoint_type="publicURL",
        service_type="dcmanager",
        auth_token=None,
        user_id=None,
        cacert=None,
        insecure=False,
        profile=None,
        auth_type="keystone",
        _client_id=None,
        _client_secret=None,
        session=None,
        cache_allowed=False,
        refresh_cache=False,
        **kwargs,
    ):
        """DC Manager communicates with Keystone to fetch necessary values."""
        if dcmanager_url and not isinstance(dcmanager_url, str):
            raise RuntimeError("DC Manager url should be a string.")

        if auth_url or session:
            if auth_type == "keystone":
                (dcmanager_url, auth_token, project_id, user_id) = authenticate(
                    dcmanager_url,
                    username,
                    api_key,
                    project_name,
                    auth_url,
                    project_id,
                    endpoint_type,
                    service_type,
                    auth_token,
                    user_id,
                    session,
                    cacert,
                    insecure,
                    cache_allowed=cache_allowed,
                    refresh_cache=refresh_cache,
                    **kwargs,
                )
            else:
                raise RuntimeError(
                    "Invalid authentication type "
                    f"[value={auth_type}, valid_values=keystone]"
                )

        if not dcmanager_url:
            dcmanager_url = _DEFAULT_DCMANAGER_URL

        if profile:
            osprofiler.profiler.init(profile)

        self.http_client = httpclient.HTTPClient(
            dcmanager_url,
            auth_token,
            project_id,
            user_id,
            cacert=cacert,
            insecure=insecure,
        )

        # Create all managers
        self.subcloud_manager = SubcloudManager(self.http_client)
        self.subcloud_group_manager = SubcloudGroupManager(
            self.http_client, self.subcloud_manager
        )
        self.subcloud_peer_group_manager = SubcloudPeerGroupManager(
            self.http_client, self.subcloud_manager
        )
        self.peer_group_association_manager = PeerGroupAssociationManager(
            self.http_client
        )
        self.subcloud_backup_manager = SubcloudBackupManager(self.http_client)
        self.subcloud_deploy_manager = SubcloudDeployManager(self.http_client)
        self.system_peer_manager = SystemPeerManager(
            self.http_client, self.subcloud_peer_group_manager
        )
        self.alarm_manager = AlarmManager(self.http_client)
        self.fw_update_manager = FwUpdateManager(self.http_client)
        self.kube_rootca_update_manager = KubeRootcaUpdateManager(self.http_client)
        self.kube_upgrade_manager = KubeUpgradeManager(self.http_client)
        self.sw_deploy_manager = SwDeployManager(self.http_client)
        self.sw_prestage_manager = SwPrestageManager(self.http_client)
        self.sw_update_options_manager = SwUpdateOptionsManager(self.http_client)
        self.strategy_step_manager = StrategyStepManager(self.http_client)
        self.sw_strategy_manager = SwStrategyManager(self.http_client)
        self.phased_subcloud_deploy_manager = PhasedSubcloudDeployManager(
            self.http_client
        )


def authenticate(
    dcmanager_url=None,
    username=None,
    api_key=None,
    project_name=None,
    auth_url=None,
    project_id=None,
    endpoint_type="publicURL",
    service_type="dcmanager",
    auth_token=None,
    user_id=None,
    session=None,
    cacert=None,
    insecure=False,
    cache_allowed=False,
    refresh_cache=False,
    **kwargs,
):
    """Get token, project_id, user_id and Endpoint."""
    user_domain_name = kwargs.get("user_domain_name")
    user_domain_id = kwargs.get("user_domain_id")
    project_domain_name = kwargs.get("project_domain_name")
    project_domain_id = kwargs.get("project_domain_id")

    if session is None:
        if auth_token:
            auth = auth_plugin.Token(
                auth_url=auth_url,
                token=auth_token,
                project_id=project_id,
                project_name=project_name,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,
                cacert=cacert,
                insecure=insecure,
            )

        elif api_key and (username or user_id):
            auth = auth_plugin.Password(
                auth_url=auth_url,
                username=username,
                user_id=user_id,
                password=api_key,
                project_id=project_id,
                project_name=project_name,
                user_domain_name=user_domain_name,
                user_domain_id=user_domain_id,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,
            )

        else:
            raise RuntimeError(
                "You must either provide a valid token or"
                "a password (api_key) and a user."
            )
        if auth:
            session = ks_session.Session(auth=auth)

    if session:
        token, cache_key = None, _cache_key(username)
        if cache_allowed:
            LOG.debug("Retrieving session auth data from cache")
            cache = utils.load_auth_session_keyring_by_name(cache_key)
            token = cache.get("token")
            dcmanager_url = cache.get("dcmanager_url")
            project_id = cache.get("project_id")
            user_id = cache.get("user_id")

        if not all([token, dcmanager_url, project_id, user_id]) or refresh_cache:
            token = session.get_token()
            if not dcmanager_url:
                dcmanager_url = session.get_endpoint(
                    service_type=service_type, interface=endpoint_type
                )
            project_id = session.get_project_id()
            user_id = session.get_user_id()

            now = datetime.datetime.now().astimezone() + datetime.timedelta(seconds=10)
            timeout = int((session.auth.auth_ref.expires - now).total_seconds())
            if cache_allowed:
                LOG.debug("Caching session auth data")
                utils.persist_auth_session_keyring(
                    name=cache_key,
                    timeout=timeout,
                    token=token,
                    dcmanager_url=dcmanager_url,
                    project_id=project_id,
                    user_id=user_id,
                )

    return dcmanager_url, token, project_id, user_id
