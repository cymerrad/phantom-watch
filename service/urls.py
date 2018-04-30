from django.conf.urls import url
from service import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^webpages/$', views.WebPageList.as_view()),
    url(r'^webpages/(?P<pk>[0-9]+)/$', views.WebPageDetail.as_view()),
    url(r'^dupas/$', views.DupaList.as_view()),
    url(r'^dupas/(?P<pk>[0-9]+)/$', views.DupaDetail.as_view()),
    url(r'^snippets/$', views.SnippetList.as_view()),
    url(r'^snippets/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)