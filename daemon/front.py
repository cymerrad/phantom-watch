from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from daemon import views

app_name = 'front'
urlpatterns = format_suffix_patterns([
    url(r'^$', views.almost_index),
    url(r'^index', views.index),
])
