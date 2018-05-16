from __future__ import unicode_literals

from django.conf.urls import url
import django_cas_ng.views as views_cas

login = views_cas.login
logout = views_cas.logout
callback = views_cas.callback

app_name = 'service'
urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^callback/$', callback, name='callback'),
]
