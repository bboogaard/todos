from rest_framework import serializers

from api.data.models import Event


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'description', 'datetime', 'event_date']


class CreateEventSerializer(serializers.Serializer):

    description = serializers.CharField()

    datetime = serializers.DateTimeField()

    def create(self, validated_data):
        event = Event(**validated_data)
        event.save()
        return event


class UpdateEventSerializer(CreateEventSerializer):

    id = serializers.IntegerField()

    def create(self, validated_data):
        id = validated_data.pop('id')
        event = Event.objects.get(id=id)
        for field, value in validated_data.items():
            setattr(event, field, value)
        event.save()
        return event
