from rest_framework import serializers
from daemon.models import Picture

class PictureSerializer(serializers.ModelSerializer):
    """
    Serializer for the Picture Model
    """
    class Meta:
        model = Picture
        fields = ('id', 'pic', 'description', 'order')
        read_only_fields = ('original_filename', )