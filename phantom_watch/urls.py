"""service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from daemon import urls as urls_d
from service import urls as urls_s
import django_cas_ng.views as views_ng

from rest_framework import routers
from rest_framework.response import Response

class ThisWillBeTheApiTitleView(routers.APIRootView):
    """
    This appears where the docstring goes!
    """
    api_root_dict = {
        "api":"http://it.must.be:8000/possible/to/force/this", # TODO
    }
    def get(self, request, *args, **kwargs):
        return Response(self.api_root_dict)


class DocumentedRouter(routers.DefaultRouter):
    APIRootView = ThisWillBeTheApiTitleView


doc_router = DocumentedRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(doc_router.urls)),
    url(r'^api/', include(urls_s.router.urls)),
    url(r'^api/', include(urls_d.router.urls), name="daemon"),
    url(r'^auth/', include('service.cas', namespace='rest_framework')) if settings.CAS_UW 
        else url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)