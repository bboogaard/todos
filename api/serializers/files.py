from rest_framework import serializers

from api.data.models import PrivateFile


class ListFileSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    class Meta:
        model = PrivateFile
        fields = ['id', 'name', 'url']

    @staticmethod
    def get_name(obj):
        return obj.file.name

    @staticmethod
    def get_url(obj):
        return obj.get_absolute_url()
