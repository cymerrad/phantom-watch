from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from service.serializers import UserSerializer, GroupSerializer, WebPageSerializer, DupaSerializer, SnippetSerializer
from service.models import WebPage, Dupa, Snippet
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

class DupaList(APIView):
    """
    List all dupas, or create a new dupa.
    """
    def get(self, request, format=None):
        dupas = Dupa.objects.all()
        serializer = DupaSerializer(dupas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = DupaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DupaDetail(APIView):
    """
    Retrieve, update or delete a dupa instance.
    """
    def get_object(self, pk):
        try:
            return Dupa.objects.get(pk=pk)
        except Dupa.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        dupa = self.get_object(pk)
        serializer = DupaSerializer(dupa)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        dupa = self.get_object(pk)
        serializer = DupaSerializer(dupa, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        dupa = self.get_object(pk)
        dupa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SnippetList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    def get(self, request, format=None):
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SnippetDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, pk):
        try:
            return Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = SnippetSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)