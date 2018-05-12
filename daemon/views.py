# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import mixins, generics
from daemon.models import Picture
from daemon.serializers import PictureSerializer

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

