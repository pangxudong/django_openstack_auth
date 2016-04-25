# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import patterns
from django.conf.urls import url

from openstack_auth import utils

utils.patch_middleware_get_user()


urlpatterns = patterns(
    'openstack_auth.views',
    url(r"^login/$", "login", name='login'),
    url(r"^logout/$", 'logout', name='logout'),
    url(r"^register/$", 'register', name='register'),# added by PXD
    url(r"^register/validate/(?P<token>[^/]+)/$", 'register_validate', name='register_validate'),# added by PXD
    url(r"^reset/$", 'reset', name='reset'),# added by PXD
    url(r"^reset/validate/(?P<token>[^/]+)/$", 'reset_validate', name='reset_validate'),# added by PXD
    url(r"^reset/done/$", 'reset_done', name='reset_done'),# added by PXD
    url(r"^reset/(?P<user_id>[^/]+)/$", 'reset_password', name='reset_password'),# added by PXD
    url(r'^switch/(?P<tenant_id>[^/]+)/$', 'switch', name='switch_tenants'),
    url(r'^switch_services_region/(?P<region_name>[^/]+)/$', 'switch_region',
        name='switch_services_region')
)
