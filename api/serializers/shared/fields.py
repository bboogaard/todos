from rest_framework import serializers


class UploadedFileField(serializers.FileField):

    def to_representation(self, value):
        return value
