#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
import os
from six.moves.urllib import parse
import sys

from neutronclient.common import exceptions as n_exceptions

from kuryr.lib import exceptions
from kuryr_libnetwork.common import config
from kuryr_libnetwork import controllers
from kuryr_libnetwork.server import start
from kuryr_libnetwork.tests.unit import base


class ConfigurationTest(base.TestKuryrBase):

    def test_defaults(self):
        basepath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../../../'))
        self.assertEqual(basepath,
                         config.CONF.pybasedir)
        self.assertEqual('/usr/libexec/kuryr',
                         config.CONF.bindir)
        self.assertEqual('http://127.0.0.1:23750',
                         config.CONF.kuryr_uri)

        self.assertEqual('http://127.0.0.1:9696',
                         config.CONF.neutron_client.neutron_uri)

        self.assertEqual('kuryr',
                         config.CONF.neutron_client.default_subnetpool_v4)

        self.assertEqual('kuryr6',
                         config.CONF.neutron_client.default_subnetpool_v6)

        self.assertEqual('http://127.0.0.1:35357/v2.0',
                         config.CONF.keystone_client.auth_uri)

    @mock.patch.object(sys, 'argv', return_value='[]')
    @mock.patch('kuryr_libnetwork.app.run')
    def test_start(self, mock_run, mock_sys_argv):
        start()
        kuryr_uri = parse.urlparse(config.CONF.kuryr_uri)
        mock_run.assert_called_once_with(kuryr_uri.hostname, 23750)

    def test_check_for_neutron_ext_support_with_ex(self):
        with mock.patch.object(controllers.app.neutron,
                            'show_extension') as mock_extension:
            ext_alias = "subnet_allocation"
            err = n_exceptions.NotFound.status_code
            ext_not_found_ex = n_exceptions.NeutronClientException(
                                                    status_code=err,
                                                    message="")
            mock_extension.side_effect = ext_not_found_ex
            ex = exceptions.MandatoryApiMissing
            self.assertRaises(ex, controllers.check_for_neutron_ext_support)
            mock_extension.assert_called_once_with(ext_alias)
