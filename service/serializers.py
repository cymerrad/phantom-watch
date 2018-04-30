from django.contrib.auth.models import User, Group
from rest_framework import serializers
from service.models import WebpageOrder

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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    url = serializers.URLField(required=True)

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)