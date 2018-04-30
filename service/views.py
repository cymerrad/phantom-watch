# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from service.serializers import UserSerializer, GroupSerializer, WebpageOrderSerializer
from service.models import WebpageOrder
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from service.permissions import IsOwnerOrReadOnly
from rest_framework import renderers
from rest_framework.response import Response
from rest_framework.decorators import action

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

class WebpageViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = WebpageOrder.objects.all()
    serializer_class = WebpageOrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                            IsOwnerOrReadOnly,)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def show(self, request, *args, **kwargs):
        webpage = self.get_object()
        return Response(webpage.pictures)


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)