from django.contrib.auth.models import User, Group
from rest_framework import serializers
from service.models import WebpageOrder
from daemon.models import Picture

class UserSerializer(serializers.ModelSerializer):
    # orders = serializers.PrimaryKeyRelatedField(many=True, queryset=WebpageOrder.objects.all())

    class Meta:
        model = User
        depth = 1
        fields = ('id', 'username', 'orders')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class WebpageOrderSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(label='ID', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    url = serializers.URLField(required=True)
    # pictures = serializers.PrimaryKeyRelatedField(many=True, queryset=Picture.objects.all())

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    class Meta:
        model = WebpageOrder
        depth = 1
        fields = ('id', 'created', 'url', 'owner', 'pictures')

class PictureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Picture Model
    """
    class Meta:
        model = Picture
        fields = ('id', 'pic', 'description', 'order')
        read_only_fields = ('original_filename', )

