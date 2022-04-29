from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers

from api.data.models import PrivateImage


class ListImageSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    thumbnail = serializers.SerializerMethodField()

    image = serializers.SerializerMethodField()

    class Meta:
        model = PrivateImage
        fields = ['id', 'name', 'url', 'thumbnail', 'image']

    @staticmethod
    def get_name(obj):
        return obj.image.name

    @staticmethod
    def get_url(obj):
        return obj.image.url

    @staticmethod
    def get_thumbnail(obj):
        return get_thumbnailer(obj.image).get_thumbnail({'size': (50, 50), 'crop': True}).url

    @staticmethod
    def get_image(obj):
        return get_thumbnailer(obj.image).get_thumbnail({'size': (400, 400), 'crop': True}).url
