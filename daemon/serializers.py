from rest_framework import serializers
from daemon.models import Picture, WebpageOrder


class PictureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Picture Model
    """
    class Meta:
        model = Picture
        fields = ('id', 'pic', 'description', 'order')
        read_only_fields = ('original_filename', )


class WebpageOrderSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(label='ID', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    url_addr = serializers.URLField(required=True)
    # pictures = serializers.PrimaryKeyRelatedField(many=True, queryset=Picture.objects.all())

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    class Meta:
        model = WebpageOrder
        depth = 1
        fields = ('id', 'created', 'url_addr', 'owner', 'pictures', 'crontab')
