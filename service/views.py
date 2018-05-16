# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from service.serializers import UserSerializer, GroupSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
