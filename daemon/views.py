# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import mixins, generics
from daemon.models import Screenshot, WebpageOrder, ScreenshotBatchParent
from daemon.serializers import ScreenshotSerializer, WebpageOrderSerializer, WebpageOrderListSerializer, \
    WebpageOrderDetailSerializer, ScreenshotBatchParentSerializer, WebpageOrderDetailZipSerializer, WebpageOrderDetailZipBatchSerializer
from rest_framework import mixins, generics, permissions, renderers
from daemon.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, renderers
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

class WebpageDetailZip(generics.ListAPIView, generics.CreateAPIView):
    """
    Retrieve some of webpages' screenshots in zip form
    """
   
    def get_serializer_class(self):
        webpage_pk = self.kwargs['pk']
        webpage = WebpageOrder.objects.all().filter(pk=webpage_pk).first()
        if webpage.shot_type == WebpageOrder.WHOLE:
            return WebpageOrderDetailZipSerializer
        else:
            return WebpageOrderDetailZipBatchSerializer

    def get_queryset(self):
        webpage_pk = self.kwargs['pk']
        webpage = WebpageOrder.objects.all().filter(pk=webpage_pk).first()

        if webpage.shot_type == WebpageOrder.WHOLE:
            queryset = Screenshot.objects.all()
        else:
            queryset = ScreenshotBatchParent.objects.all()

        queryset = queryset.filter(order=webpage_pk)

        ids = self.request.query_params.get('ids', None)
        if ids is not None:
            queryset = queryset.filter(pk__in=ids)

        return queryset

def almost_index(request):
    return redirect("/index")

def index(request):
    if request.user.is_authenticated:
        return render(request, 'daemon/index.jinja', context={'user':request.user, 'request':request})
    else:
        return render(request, 'daemon/index.jinja', context={'request':request})
