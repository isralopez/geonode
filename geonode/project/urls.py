# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .views import ProjectUpdateView, GeocyberUploadView

js_info_dict = {
    'packages': ('geonode.project',),
}

urlpatterns = patterns('geonode.project.views',
                       url(r'^$',
                           TemplateView.as_view(template_name='documents/project_list.html'),
                           name='project_browse'),

                       url(r'^(?P<docid>\d+)/?$',
                           'project_detail',
                           name='project_detail'),
                       url(r'^(?P<docid>\d+)/download/?$',
                           'project_download',
                           name='project_download'),
                       url(r'^(?P<docid>\d+)/replace$',
                           login_required(ProjectUpdateView.as_view()),
                           name="project_replace"),
                       url(r'^(?P<docid>\d+)/remove$',
                           'project_remove',
                           name="project_remove"),

                       url(r'^search/?$',
                           'document_search_page',
                           name='document_search_page'),

                       url(r'^(?P<docid>\d+)/metadata$',
                           'project_metadata',
                           name='project_metadata'),
                       url(r'^upload/geocyber/?$',
                           login_required(GeocyberUploadView.as_view()),
                           name='geocyber_upload'),
                       )
