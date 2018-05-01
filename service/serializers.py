from django.contrib.auth.models import User, Group
from rest_framework import serializers
from service.models import WebpageOrder
from daemon.models import Picture

class UserSerializer(serializers.ModelSerializer):
    orders = serializers.PrimaryKeyRelatedField(many=True, queryset=WebpageOrder.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'orders')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class WebpageOrderSerializer(serializers.Serializer): 
    owner = serializers.ReadOnlyField(source='owner.username')
    url = serializers.URLField(required=True)
    pictures = serializers.PrimaryKeyRelatedField(many=True, queryset=Picture.objects.all())

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    class Meta:
        model = WebpageOrder
        fields = ('created', 'url', 'owner', 'pictures')

    