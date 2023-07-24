#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from requests_toolbelt import MultipartEncoder

from dcmanagerclient.api import base
from dcmanagerclient.api.base import get_json

BASE_URL = '/phased-subcloud-deploy/'


class phased_subcloud_deploy_manager(base.ResourceManager):
    resource_class = base.Subcloud

    def json_to_resource(self, json_object):
        return self.resource_class.from_payload(self, json_object)

    def _request_method(self, method, url, body, headers):
        method = method.lower()
        if method not in ("post", "patch", "put", "get", "delete"):
            raise ValueError("Invalid request method: %s" % method)
        return getattr(self.http_client, method)(url, body, headers)

    def _deploy_operation(self, url, body, data, method='post'):
        fields = dict()
        for k, v in body.items():
            fields.update({k: (v, open(v, 'rb'),)})
        fields.update(data)
        enc = MultipartEncoder(fields=fields)
        headers = {'content-type': enc.content_type}
        resp = self._request_method(method, url, enc, headers)
        if resp.status_code != 200:
            self._raise_api_exception(resp)
        json_object = get_json(resp)
        resource = [self.json_to_resource(json_object)]
        return resource

    def subcloud_deploy_create(self, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        return self._deploy_operation(BASE_URL, files, data)

    def subcloud_deploy_install(self, subcloud_ref, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        url = BASE_URL + "%s/install" % subcloud_ref
        return self._deploy_operation(url, files, data, method='patch')

    def subcloud_deploy_bootstrap(self, subcloud_ref, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        url = BASE_URL + "%s/bootstrap" % subcloud_ref
        return self._deploy_operation(url, files, data, method='patch')

    def subcloud_deploy_config(self, subcloud_ref, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        url = BASE_URL + "%s/configure" % subcloud_ref
        return self._deploy_operation(url, files, data, method='patch')

    def subcloud_deploy_complete(self, subcloud_ref):
        url = BASE_URL + "%s/complete" % subcloud_ref
        return self._deploy_operation(url, {}, {}, method='patch')

    def subcloud_deploy_abort(self, subcloud_ref, **kwargs):
        # Currently it's not passed neither data or files to abort,
        # so we pass an empty dict to use the _deploy_operation function
        data = kwargs.get('data', {})
        files = kwargs.get('files', {})
        url = BASE_URL + "%s/abort" % subcloud_ref
        return self._deploy_operation(url, files, data, method='patch')

    def subcloud_deploy_resume(self, subcloud_ref, **kwargs):
        data = kwargs.get('data')
        files = kwargs.get('files')
        url = BASE_URL + "%s/resume" % subcloud_ref
        return self._deploy_operation(url, files, data, method='patch')
