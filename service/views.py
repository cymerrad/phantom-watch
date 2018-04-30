from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from service.serializers import UserSerializer, GroupSerializer, WebPageSerializer
from service.models import WebPage
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class WebPageList(APIView):
    """
    List all WebPages, or create a new WebPage.
    """
    def get(self, request, format=None):
        webPages = WebPage.objects.all()
        serializer = WebPageSerializer(webPages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WebPageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class WebPageDetail(APIView):
    """
    Retrieve, update or delete a WebPage.
    """
    def get_object(self, pk):
        try:
            return WebPage.objects.get(pk=pk)
        except WebPage.DoesNotExist:
            raise Http404
            
    def get(self, request, pk, format=None):
        webpage = self.get_object(pk)
        serializer = WebPageSerializer(webpage)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        webpage = self.get_object(pk)
        serializer = WebPageSerializer(webpage, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        webpage = self.get_object(pk)
        webpage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
