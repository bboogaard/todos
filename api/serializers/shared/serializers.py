import os.path

from django.utils.text import slugify
from rest_framework import serializers

from api.serializers.shared.fields import UploadedFileField


class ImportSerializer(serializers.Serializer):

    file = UploadedFileField()


class ExportSerializer(serializers.Serializer):

    filename = serializers.CharField()

    @property
    def export_file_extension(self):
        return self.context.get('export_file_extension')

    def validate_filename(self, data):
        filename, ext = os.path.splitext(data)
        return slugify(filename) + self.export_file_extension
