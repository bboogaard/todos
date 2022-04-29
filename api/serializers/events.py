import datetime

import pytz
from dataclasses import asdict
from django.conf import settings
from rest_framework import serializers

from api.data.models import Event
from services.factory import CalendarServiceFactory


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ['id', 'description', 'datetime', 'event_date']


class CreateEventSerializer(serializers.Serializer):

    description = serializers.CharField()

    date = serializers.DateField()

    time = serializers.TimeField()

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        data['datetime'] = pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime.combine(
            data.pop('date'), data.pop('time')
        ))
        return data

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


class WeeksSerializer(serializers.Serializer):

    year = serializers.IntegerField(write_only=True)

    month = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        return attrs

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, validated_data):
        weeks = CalendarServiceFactory.create().get_weeks(validated_data['year'], validated_data['month'])
        return {
            'weeks': [asdict(week) for week in weeks]
        }
