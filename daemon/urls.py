from django.conf.urls import url
from daemon import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'webpages', views.WebpageViewSet)
router.register(r'pictures', views.PictureViewSet)

urlpatterns = [
    url(r'^pictures/$', views.PictureList.as_view()),
    url(r'^pictures/(?P<pk>[0-9]+)/$', views.PictureDetail.as_view()),
    url(r'^webpages/$', views.WebpageList.as_view()),
    url(r'^webpages/(?P<pk>[0-9]+)/$', views.WebpageDetail.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
