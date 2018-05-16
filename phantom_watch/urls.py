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
from daemon import views as views_d
from service import views
import django_cas_ng.views as views_ng

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'webpages', views_d.WebpageViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^', include('service.urls')),
    url(r'^', include('daemon.urls')),
    url(r'^api-auth/', include('service.cas', namespace='rest_framework')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)