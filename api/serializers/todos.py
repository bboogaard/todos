from django.utils.timezone import now
from rest_framework import serializers

from api.data.models import Todo


class ListTodoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Todo
        fields = ['id', 'description']


class CreateTodoSerializer(serializers.Serializer):

    description = serializers.CharField()

    def create(self, validated_data):
        return Todo(description=validated_data['description'], activate_date=now())


class UpdateTodoSerializer(CreateTodoSerializer):

    id = serializers.IntegerField()

    def create(self, validated_data):
        return Todo(id=validated_data['id'], description=validated_data['description'])
