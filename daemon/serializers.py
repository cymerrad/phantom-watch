from rest_framework import serializers
from daemon.models import Screenshot, WebpageOrder, ScreenshotBatchChild, ScreenshotBatchParent
import logging
from django.shortcuts import reverse

logger = logging.getLogger('django')

class ScreenshotSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the Screenshot Model
    """
    class Meta:
        model = Screenshot
        fields = ('id', 'pic', 'description', 'order')
        read_only_fields = ('original_filename', )

class ScreenshotBatchParentSerializer(serializers.ModelSerializer):
    """
    Serializer for the ScreenshotBatchParent Model
    """
    self_url = serializers.HyperlinkedIdentityField(view_name='daemon:screenshotbatchparent-detail', format='html')
    class Meta:
        model = ScreenshotBatchParent
        fields = ('id', 'self_url', 'children', 'description', 'order')
        depth = 1

class ScreenshotBatchChildSerializer(serializers.ModelSerializer):
    """
    Serializer for the ScreenshotBatchChild Model
    """
    class Meta:
        model = ScreenshotBatchChild
        fields = ('id', 'pic', 'description')
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
    self_url = serializers.HyperlinkedIdentityField(view_name='daemon:webpage-detail', format='html')
    owner = serializers.ReadOnlyField(source='owner.username')
    target_url = serializers.URLField(required=True)
    screenshots_count = serializers.SerializerMethodField()
    shot_type = serializers.ChoiceField(choices=WebpageOrder.TYPE_CHOICES, initial=WebpageOrder.WHOLE)
    resolution = serializers.ChoiceField(choices=WebpageOrder.RESOLUTION_CHOICES, initial=WebpageOrder.RESOLUTION_DEFAULT)
    clear_view = serializers.BooleanField(help_text='I will try to get past those iritating ads or cookie reminders.', initial=False)
    username = serializers.CharField(write_only=True, required=False, help_text='Username to be used for logging in to the site.', initial=None)
    password = serializers.CharField(write_only=True, required=False, help_text='Password to be used for logging in.', initial=None, style={'input_type': 'password'})

    def validate(self, data):
        """
        We have to receive both username and password or neither of them
        """
        if ('username' in data.keys()) ^ ('password' in data.keys()):
            raise serializers.ValidationError("Cannot provide username without password or vice-versa")

        return data

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    def get_screenshots_count(self, obj):
        return obj.screenshots.count() if obj.is_whole_type() else obj.screenshots_batch.count()

    class Meta:
        model = WebpageOrder
        depth = 0
        fields = ('id', 'self_url', 'created', 'target_url', 'owner', 'screenshots_count', 'crontab', 
            'shot_type', 'resolution', 'username', 'password', 'clear_view')


class WebpageOrderDetailSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(label='ID', read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    target_url = serializers.URLField(read_only=True)
    clear_view = serializers.BooleanField(help_text='I will try to get past those iritating ads or cookie reminders.')
    shot_type = serializers.ChoiceField(choices=WebpageOrder.TYPE_CHOICES, read_only=True)
    resolution = serializers.ChoiceField(choices=WebpageOrder.RESOLUTION_CHOICES, read_only=True)
    username = serializers.CharField(write_only=True, required=False, help_text='Username to be used for logging in to the site.', initial=None)
    password = serializers.CharField(write_only=True, required=False, help_text='Password to be used for logging in.', initial=None, style={'input_type': 'password'})
    credentials = serializers.SerializerMethodField()
    clear_credentials = serializers.BooleanField(help_text='Delete stored credentials?', initial=False, write_only=True)

    def create(self, validated_data):
        """
        Create and return a new `WebpageOrder` instance, given the validated data.
        """
        return WebpageOrder.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if validated_data['clear_credentials']:
            setattr(instance, 'username', '')
            setattr(instance, 'password', '')
        instance.save()
        return super(WebpageOrderDetailSerializer, self).update(instance, validated_data)

    def validate(self, data):
        """
        We have to receive both username and password or neither of them
        """
        if ('username' in data.keys()) ^ ('password' in data.keys()):
            raise serializers.ValidationError("Cannot provide username without password or vice-versa")

        return data

    def get_credentials(self, obj):
        if (obj.password is not "") and (obj.username is not ""):
            return True
        return False



    class Meta:
        model = WebpageOrder
        depth = 1
        fields = ('id', 'created', 'target_url', 'owner', 'screenshots', 'screenshots_batch', 'crontab', 'failures',
            'shot_type', 'resolution', 'username', 'password', 'clear_view', 'clear_credentials', 'credentials')