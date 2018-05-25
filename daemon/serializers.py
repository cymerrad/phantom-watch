from rest_framework import serializers
from daemon.models import Screenshot, WebpageOrder
import logging

logger = logging.getLogger('django')

class ScreenshotSerializer(serializers.ModelSerializer):
    """
    Serializer for the Screenshot Model
    """
    class Meta:
        model = Screenshot
        fields = ('id', 'pic', 'description', 'order')
        read_only_fields = ('original_filename', )


class WebpageOrderSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(label='ID', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    url_addr = serializers.URLField(required=True)
    # pictures = serializers.PrimaryKeyRelatedField(many=True, queryset=Screenshot.objects.all())
    pictures = serializers.HyperlinkedIdentityField(many=True, view_name='picture-detail', format='html')

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    class Meta:
        model = WebpageOrder
        depth = 0
        fields = ('id', 'created', 'url_addr', 'owner', 'pictures', 'crontab')

class WebpageOrderListSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(label='ID', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    url_addr = serializers.URLField(required=True)
    pictures_count = serializers.SerializerMethodField()
    shot_type = serializers.ChoiceField(choices=WebpageOrder.TYPE_CHOICES, initial=WebpageOrder.WHOLE)
    resolution = serializers.ChoiceField(choices=WebpageOrder.RESOLUTION_CHOICES, initial=WebpageOrder.RESOLUTION_DEFAULT)
    clear_view = serializers.BooleanField(help_text='I will try to get past those iritating ads or cookie reminders.')
    username = serializers.CharField(write_only=True, required=False, help_text='Username to be used for logging in to the site.')
    password = serializers.CharField(write_only=True, required=False, help_text='Did you expect an API view to hide passwords?')

    def validate(self, data):
        """
        We have to receive both username and password or neither of them
        """
        logger.info(data)
        if ('username' in data.keys()) ^ ('password' in data.keys()):
            raise serializers.ValidationError("Cannot provide username without password or vice-versa")

        return data

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    class Meta:
        model = WebpageOrder
        depth = 0
        fields = ('id', 'created', 'url_addr', 'owner', 'pictures_count', 'crontab', 
        'shot_type', 'resolution', 'username', 'password', 'clear_view')

    def get_pictures_count(self, obj):
        return obj.pictures.count()

class WebpageOrderDetailSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(label='ID', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    url_addr = serializers.URLField(required=True)
    # pictures = serializers.PrimaryKeyRelatedField(many=True, queryset=Screenshot.objects.all())
    # pictures = serializers.HyperlinkedIdentityField(many=True, view_name='picture-detail', format='html')

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    class Meta:
        model = WebpageOrder
        depth = 1
        fields = ('id', 'created', 'url_addr', 'owner', 'pictures', 'crontab', 'failures')