# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import mixins, generics
from daemon.models import Picture, WebpageOrder
from daemon.serializers import PictureSerializer, WebpageOrderSerializer
from rest_framework import mixins, generics, permissions, renderers
from daemon.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets

class PictureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve pictures
    """
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer
    @action(detail=True, url_name='picture-detail')
    def show(self, *args, **kwargs):
        return super(PictureViewSet, self).get(args, kwargs)

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


#
#
#
# in case anything down here becomes useful later
# just remember about viewset.ViewSetMixin

class PictureList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    List all Pictures, or create a new Picture.
    """
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class PictureDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete a Picture.
    """
    queryset = Picture.objects.all()
    serializer_class = PictureSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class WebpageList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    """
    List all Webpages, or create a new Webpage.
    """
    queryset = WebpageOrder.objects.all()
    serializer_class = WebpageOrderSerializer
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
    serializer_class = WebpageOrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
