from django.conf.urls import url, include
from daemon import views as views_d
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from collections import OrderedDict

app_name='daemon'

class ExtendableRouter(routers.DefaultRouter):
    def get_api_root_view(self, api_urls=None):
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        # manualy add API's here
        api_root_dict['webpages'] = 'webpage-list'

        return self.APIRootView.as_view(api_root_dict=api_root_dict)


router = ExtendableRouter()
router.register(r'screenshots', views_d.ScreenshotViewSet)
router.register(r'screenshots_batch', views_d.ScreenshotBatchViewSet)

urlpatterns = [
    url(r'^webpages/$', views_d.WebpageList.as_view(), name='webpage-list'),
    url(r'^webpages/(?P<pk>[0-9]+)/$', views_d.WebpageDetail.as_view(), name='webpage-detail'),
]
urlpatterns = format_suffix_patterns(urlpatterns) + [
    url(r'^', include(router.urls)),
]
