from rest_framework import serializers

from api.data.models import Widget


class ListWidgetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Widget
        fields = ['id', 'title', 'is_enabled', 'position', 'refresh_interval']


class UpdateWidgetSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    is_enabled = serializers.BooleanField(required=False)

    position = serializers.IntegerField(min_value=0)

    refresh_interval = serializers.IntegerField(min_value=0, required=False, allow_null=True)

    def create(self, validated_data):
        print(validated_data)
        widget = Widget.objects.get(pk=validated_data['id'])
        widget.is_enabled = validated_data['is_enabled']
        widget.position = validated_data['position']
        widget.refresh_interval = validated_data['refresh_interval']
        widget.save()
        return widget
