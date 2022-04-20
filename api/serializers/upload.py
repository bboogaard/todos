import magic
from rest_framework import serializers

from api.data.models import PrivateFile, PrivateImage


class UploadSerializer(serializers.Serializer):

    file = serializers.FileField()

    def create(self, validated_data):
        file = validated_data['file']
        model = self.get_model(file)
        instance = model()
        instance.save_file(file)
        return instance

    @staticmethod
    def get_model(file):
        mimetype = magic.from_buffer(file.read(), mime=True)
        file.seek(0)
        return PrivateImage if mimetype.startswith('image') else PrivateFile
