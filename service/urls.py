from django.conf.urls import url
from service import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'groups', views.GroupViewSet)
router.register(r'users', views.UserViewSet)

# urlpatterns = [
# ]
# urlpatterns = format_suffix_patterns(urlpatterns)