from rest_framework import serializers

from api.data.models import Gallery


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = ['id', 'name']


class UpdateGallerySerializer(serializers.Serializer):

    id = serializers.IntegerField()

    active = serializers.BooleanField()

    def create(self, validated_data):
        return Gallery(id=validated_data['id'], active=validated_data['active'])
