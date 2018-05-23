from django.conf.urls import url, include
from daemon import views as views_d
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

app_name='daemon'
router = routers.DefaultRouter()
router.register(r'pictures', views_d.PictureViewSet)

urlpatterns = [
    url(r'^webpages/$', views_d.WebpageList.as_view(), name='webpage-list'),
    url(r'^webpages/(?P<pk>[0-9]+)/$', views_d.WebpageDetail.as_view(), name='webpage-detail'),
]
urlpatterns = format_suffix_patterns(urlpatterns) + [
    url(r'^', include(router.urls)),
]
