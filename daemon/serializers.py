from rest_framework import serializers
from daemon.models import Screenshot, WebpageOrder, ScreenshotBatchChild, ScreenshotBatchParent, ZippingOrder
import logging
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
import re
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('django')

class ScreenshotSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = ScreenshotBatchParent
        fields = ('id', 'children', 'description', 'order')
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
    clear_view = serializers.BooleanField(help_text='I will try to get past those irritating ads or cookie reminders.', initial=False)
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
        return max(obj.screenshots.count(), obj.screenshots_batch.count())

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
    screenshots_batch = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='daemon:screenshot_batch-detail')


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


SCREENSHOT_RANGES_REGEXP = r'^((?:[, ]*)((\d+-\d+)|\d+)(?:[, ]*))+$'
scr_ranges_re = re.compile(SCREENSHOT_RANGES_REGEXP)
def validate_screenshot_ranges(input):
    if not scr_ranges_re.match(input):
        raise ValidationError(
            _('%(value)s is not a valid range list'),
            params={'value': input},
        )

class WebpageOrderDetailZipSerializer(serializers.ModelSerializer):
    screenshot_ranges = serializers.CharField(write_only=True, required=False, validators=[validate_screenshot_ranges],
        help_text="E.g. '1-15,17,18,19,21-100' for omitting 16 and 20 in a very weird way. Commas and spaces inbetween don't matter.")
    all_screenshots = serializers.BooleanField(write_only=True, default=False)

    def create(self, validated_data):
        """
        Create new task for zipping the screenshots, given the validated data.
        """
        return ZippingOrder.objects.create(**validated_data)

class WebpageOrderDetailZipBatchSerializer(WebpageOrderDetailZipSerializer):
    screenshot_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=ScreenshotBatchParent.objects.all()),
        write_only=True,
    )

    class Meta:
        fields = ('id', 'created', 'description', 'order', 'screenshot_list', 'all_screenshots', 'screenshot_ranges')
        read_only_fields = ('description', 'order',)
        model = ScreenshotBatchParent

class WebpageOrderDetailZipWholeSerializer(WebpageOrderDetailZipSerializer):
    screenshot_list = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Screenshot.objects.all()),
        write_only=True,
    )

    class Meta:
        fields = ('id', 'created', 'description', 'order', 'screenshot_list', 'all_screenshots', 'screenshot_ranges')
        read_only_fields = ('description', 'order',)
        model = Screenshot

class ZippingOrderSerializer(serializers.ModelSerializer):
    self_url = serializers.HyperlinkedIdentityField(view_name='daemon:zipping_order-detail', format='html')

    class Meta:
        fields = ('id', 'self_url', 'created', 'order', 'screenshot_list', 'all_screenshots', 'screenshot_ranges', 'zip_file', 'error', 'finished')
        read_only_fields = ('description', 'order',)
        model = ZippingOrder