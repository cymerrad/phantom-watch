from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from service.serializers import UserSerializer, GroupSerializer, WebPageSerializer
from service.models import WebPage
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


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

@csrf_exempt
def webpages_list(request):
    """
    List all code WebPages, or create a new WebPage.
    """
    if request.method == 'GET':
        webPages = WebPage.objects.all()
        serializer = WebPageSerializer(webPages, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = WebPageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def webpage_detail(request, pk):
    """
    Retrieve, update or delete a WebPage.
    """
    try:
        webPage = WebPage.objects.get(pk=pk)
    except webPage.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = WebPageSerializer(webPage)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = WebPageSerializer(webPage, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        webPage.delete()
        return HttpResponse(status=204)