from django.conf.urls import url
from service import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^pictures/$', views.PictureList.as_view()),
    url(r'^pictures/(?P<pk>[0-9]+)/$', views.PictureDetail.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)