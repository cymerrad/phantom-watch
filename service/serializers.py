from django.contrib.auth.models import User, Group
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    # orders = serializers.PrimaryKeyRelatedField(many=True, queryset=WebpageOrder.objects.all())

    class Meta:
        model = User
        depth = 1
        fields = ('id', 'username', 'orders', 'zipping_orders')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')
