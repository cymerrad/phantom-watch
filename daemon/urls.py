from django.conf.urls import url
from daemon import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

urlpatterns = [
    url(r'^pictures/$', views.PictureList.as_view()),
    url(r'^pictures/(?P<pk>[0-9]+)/$', views.PictureDetail.as_view()),
    url(r'^webpages/$', views.WebpageList.as_view()),
    url(r'^webpages/(?P<pk>[0-9]+)/$', views.WebpageDetail.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)

# router = routers.DefaultRouter()
# router.register(r'^pictures/$', views.PictureList.as_view(), base_name="pictures"),
# router.register(r'^pictures/(?P<pk>[0-9]+)/$', views.PictureDetail.as_view(), base_name="pictures/<pk>"),
# router.register(r'^webpages/$', views.WebpageList.as_view(), base_name="webpages"),
# router.register(r'^webpages/(?P<pk>[0-9]+)/$', views.WebpageDetail.as_view(), base_name="webpages/<pk>"),