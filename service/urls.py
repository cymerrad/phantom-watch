from django.conf.urls import url
from service import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # url(r'^webpages/$', views.WebpageOrderList.as_view()),
    # url(r'^webpages/(?P<pk>[0-9]+)/$', views.WebpageOrderDetail.as_view()),
    # url(r'^users/$', views.UserList.as_view()),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'^pictures/$', views.PictureList.as_view()),
    url(r'^pictures/(?P<pk>[0-9]+)/$', views.PictureDetail.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)