from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from service.serializers import UserSerializer, GroupSerializer, WebpageOrderSerializer
from service.models import WebpageOrder
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from service.permissions import IsOwnerOrReadOnly

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class WebpageOrderList(mixins.ListModelMixin,
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

class WebpageOrderDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    """
    Retrieve, update or delete a Webpage.
    """
    queryset = WebpageOrder.objects.all()
    serializer_class = WebpageOrderSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
