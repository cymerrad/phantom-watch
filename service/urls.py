from django.conf.urls import url
from service import views

urlpatterns = [
    url(r'^webpages/$', views.webpages_list),
    url(r'^webpages/(?P<pk>[0-9]+)/$', views.webpage_detail),
]