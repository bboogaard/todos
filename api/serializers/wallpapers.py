from rest_framework import serializers

from api.data.models import Gallery, Wallpaper


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = ['id', 'name']


class ListWallpaperSerializer(serializers.ModelSerializer):

    gallery = GallerySerializer()

    image = serializers.SerializerMethodField()

    class Meta:
        model = Wallpaper
        fields = ['id', 'gallery', 'image', 'position']

    @staticmethod
    def get_image(obj):
        return obj.get_image_url()


class CreateWallpaperSerializer(serializers.Serializer):

    gallery = serializers.IntegerField()

    image = serializers.FileField()

    position = serializers.IntegerField(min_value=0)

    def create(self, validated_data):
        gallery = Gallery.objects.get(pk=validated_data['gallery'])
        wallpaper = Wallpaper(gallery=gallery, position=validated_data['position'])
        fh = validated_data['image']
        wallpaper.image.save(fh.name, fh)
        wallpaper.save()
        return wallpaper


class UpdateWallpaperSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    gallery = serializers.IntegerField()

    position = serializers.IntegerField(min_value=0)

    def create(self, validated_data):
        gallery = Gallery.objects.get(pk=validated_data['gallery'])
        wallpaper = Wallpaper.objects.get(pk=validated_data['id'])
        wallpaper.gallery = gallery
        wallpaper.position = validated_data['position']
        wallpaper.save()
        return wallpaper
