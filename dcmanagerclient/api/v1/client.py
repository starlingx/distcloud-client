# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
# Copyright 2016 - Ericsson AB.
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

import keystoneauth1.identity.generic as auth_plugin
from keystoneauth1 import session as ks_session

from dcmanagerclient.api import httpclient
from dcmanagerclient.api.v1 import alarm_manager as am
from dcmanagerclient.api.v1 import subcloud_manager as sm
from dcmanagerclient.api.v1 import sw_update_manager as sum
from dcmanagerclient.api.v1 import sw_update_options_manager as suom


import osprofiler.profiler

import six


_DEFAULT_DCMANAGER_URL = "http://localhost:8119/v1.0"


class Client(object):
    """Class where the communication from KB to Keystone happens."""

    def __init__(self, dcmanager_url=None, username=None, api_key=None,
                 project_name=None, auth_url=None, project_id=None,
                 endpoint_type='publicURL', service_type='dcmanager',
                 auth_token=None, user_id=None, cacert=None, insecure=False,
                 profile=None, auth_type='keystone', client_id=None,
                 client_secret=None, session=None, **kwargs):
        """DC Manager communicates with Keystone to fetch necessary values."""
        if dcmanager_url and not isinstance(dcmanager_url, six.string_types):
            raise RuntimeError('DC Manager url should be a string.')

        if auth_url or session:
            if auth_type == 'keystone':
                (dcmanager_url, auth_token, project_id, user_id) = (
                    authenticate(
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
                        **kwargs
                    )
                )
            else:
                raise RuntimeError(
                    'Invalid authentication type [value=%s, valid_values=%s]'
                    % (auth_type, 'keystone')
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
            insecure=insecure
        )

        # Create all managers
        self.subcloud_manager = sm.subcloud_manager(self.http_client)
        self.alarm_manager = am.alarm_manager(self.http_client)
        self.sw_update_manager = sum.sw_update_manager(self.http_client)
        self.sw_update_options_manager = \
            suom.sw_update_options_manager(self.http_client)
        self.strategy_step_manager = sum.strategy_step_manager(
            self.http_client)


def authenticate(dcmanager_url=None, username=None,
                 api_key=None, project_name=None, auth_url=None,
                 project_id=None, endpoint_type='publicURL',
                 service_type='dcmanager', auth_token=None, user_id=None,
                 session=None, cacert=None, insecure=False, **kwargs):
    """Get token, project_id, user_id and Endpoint."""
    if project_name and project_id:
        raise RuntimeError(
            'Only project name or project id should be set'
        )

    if username and user_id:
        raise RuntimeError(
            'Only user name or user id should be set'
        )
    user_domain_name = kwargs.get('user_domain_name')
    user_domain_id = kwargs.get('user_domain_id')
    project_domain_name = kwargs.get('project_domain_name')
    project_domain_id = kwargs.get('project_domain_id')

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
                insecure=insecure)

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
                project_domain_id=project_domain_id)

        else:
            raise RuntimeError('You must either provide a valid token or'
                               'a password (api_key) and a user.')
        if auth:
            session = ks_session.Session(auth=auth)

    if session:
        token = session.get_token()
        project_id = session.get_project_id()
        user_id = session.get_user_id()
        if not dcmanager_url:
            dcmanager_url = session.get_endpoint(
                service_type=service_type,
                interface=endpoint_type)

    return dcmanager_url, token, project_id, user_id
