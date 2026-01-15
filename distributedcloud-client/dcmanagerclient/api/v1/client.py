# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
# Copyright 2016 - Ericsson AB.
# Copyright (c) 2017-2026 Wind River Systems, Inc.
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
from urllib.parse import urlparse

import keystoneauth1.identity.generic as auth_plugin
from keystoneauth1 import session as ks_session
import osprofiler.profiler
from platform_util.oidc import oidc_utils

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
from dcmanagerclient import exceptions

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
        project_id="admin",
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
            elif auth_type == "oidc":
                if not username:
                    raise RuntimeError("Username is required for OIDC authentication")

                try:
                    (dcmanager_url, auth_token) = _get_oidc_data(
                        username,
                        auth_url,
                        endpoint_type,
                        service_type,
                    )
                except Exception as e:
                    raise RuntimeError(f"OIDC authentication failed: {e}") from e
            else:
                raise RuntimeError(
                    "Invalid authentication type "
                    f"[value={auth_type}, valid_values=keystone,oidc]"
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
            auth_type=auth_type,
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
    token = None
    verify = False if insecure else (cacert if cacert else True)

    if session is None:
        if auth_token:
            auth = auth_plugin.Token(
                auth_url=auth_url,
                token=auth_token,
                project_id=project_id,
                project_name=project_name,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,
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
                "You must either provide a valid token or "
                "a password (api_key) and a username."
            )
        session = ks_session.Session(auth=auth, verify=verify)

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


def _get_oidc_data(username, auth_url, endpoint_type, service_type):
    """Get OIDC token and dcmanager URL.

    Args:
        username: Username for OIDC token lookup
        auth_url: OS_AUTH_URL for service URL construction
        endpoint_type: Interface type (publicURL, internalURL, adminURL)
        service_type: Service type (dcmanager)

    Returns:
        tuple: (dcmanager_url, oidc_token)
    """
    dcmanager_url = _build_service_url(auth_url, service_type, endpoint_type)

    # Client should ALWAYS read OIDC Token from $KUBECONFIG file, no caching
    oidc_token = oidc_utils.get_oidc_token(username)
    if not oidc_token:
        raise exceptions.DCManagerClientException(
            f"No OIDC token found for user '{username}' in kubeconfig"
        )

    return dcmanager_url, oidc_token


def _build_service_url(auth_url, service_type, endpoint_type):
    """Build service URL from auth_url and service parameters.

    Args:
        auth_url: OS_AUTH_URL containing the IP address
        service_type: Service type (e.g., 'dcmanager')
        endpoint_type: Interface type (publicURL, internalURL, adminURL)

    Returns:
        str: Complete service URL
    """
    if not auth_url:
        raise exceptions.DCManagerClientException(
            "OS_AUTH_URL is required for OIDC authentication"
        )

    # Parse IP address from auth_url
    parsed = urlparse(auth_url)
    ip_address = parsed.hostname

    if not ip_address:
        raise exceptions.DCManagerClientException(
            f"Cannot extract IP address from OS_AUTH_URL: {auth_url}"
        )

    # Map endpoint types to interface names
    interface_map = {
        "publicURL": "public",
        "internalURL": "internal",
        "adminURL": "admin",
    }

    interface = interface_map.get(endpoint_type)

    # Service port and path mappings
    service_ports = {
        "public": {"dcmanager": 8119},
        "internal": {"dcmanager": 8119},
        "admin": {"dcmanager": 8120},
    }

    service_paths = {
        "public": {"dcmanager": "/v1.0"},
        "internal": {"dcmanager": "/v1.0"},
        "admin": {"dcmanager": "/v1.0"},
    }

    # Determine protocol
    # HTTPS should always be enabled for public endpoints when using OIDC
    if interface in ["public", "admin"]:
        protocol = "https"
    else:
        protocol = "http"

    # Get port and path
    port = service_ports.get(interface, {}).get(service_type)
    path = service_paths.get(interface, {}).get(service_type)

    if not port or not path:
        raise exceptions.DCManagerClientException(
            f"No port/path mapping for service {service_type} on "
            f"interface {interface}"
        )

    # Format IP address for URL (IPv6 needs brackets)
    if ":" in ip_address and not ip_address.startswith("["):
        formatted_ip = f"[{ip_address}]"
    else:
        formatted_ip = ip_address

    return f"{protocol}://{formatted_ip}:{port}{path}"
