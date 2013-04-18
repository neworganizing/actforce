from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from actforce.apps.base.views import PreferencesView, SFAuthView
from actforce.apps.mover.views import MoverView, PageListView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social_auth.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout',{'next_page': '/'}, name='logout'),
    url(r'^$', RedirectView.as_view(url='/mover/')),
    url(r'^preferences/$', PreferencesView.as_view(), name='preferences'),
    url(r'^sfauth/$', SFAuthView.as_view(), name='salesforceauth'),
    url(r'^mover/$', PageListView.as_view(), name='mover_pagelist'),
    url(r'^mover/(?P<pagename>[0-9A-Za-z_\-]+)/$', MoverView.as_view(), name='mover_pageroot'),
    url(r'^mover/(?P<pagename>[0-9A-Za-z_\-]+)/(?P<actionid>[0-9]+)$', MoverView.as_view(), name='mover_action')
)

if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )