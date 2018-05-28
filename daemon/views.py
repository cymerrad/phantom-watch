# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import mixins, generics
from daemon.models import Screenshot, WebpageOrder, ScreenshotBatchParent
from daemon.serializers import ScreenshotSerializer, WebpageOrderSerializer, WebpageOrderListSerializer, WebpageOrderDetailSerializer, ScreenshotBatchParentSerializer
from rest_framework import mixins, generics, permissions, renderers
from daemon.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from django.shortcuts import render, redirect

class ScreenshotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve pictures
    """
    queryset = Screenshot.objects.all()
    serializer_class = ScreenshotSerializer

class ScreenshotBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve pictures
    """
    queryset = ScreenshotBatchParent.objects.all()
    serializer_class = ScreenshotBatchParentSerializer


class WebpageList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    List all Webpages, or create a new Webpage.
    """
    queryset = WebpageOrder.objects.all()
    serializer_class = WebpageOrderListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class WebpageDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete a Webpage.
    """
    queryset = WebpageOrder.objects.all()
    serializer_class = WebpageOrderDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

def almost_index(request):
    return redirect("/index")

def index(request):
    if request.user.is_authenticated:
        return render(request, 'daemon/index.jinja', context={'user':request.user, 'request':request})
    else:
        return render(request, 'daemon/index.jinja', context={'request':request})
