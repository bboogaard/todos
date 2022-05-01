import os.path

from django.utils.text import slugify
from rest_framework import serializers

from api.serializers.shared.fields import UploadedFileField


class ImportFileSerializer(serializers.Serializer):

    file = UploadedFileField()


class ExportFileSerializer(serializers.Serializer):

    filename = serializers.CharField()

    def validate_filename(self, data):
        filename, ext = os.path.splitext(data)
        return slugify(filename) + '.zip'
