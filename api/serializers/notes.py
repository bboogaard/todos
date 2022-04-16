from rest_framework import serializers

from api.data.models import Note


class ListNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ['id', 'text']


class CreateNoteSerializer(serializers.Serializer):

    text = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        note = Note(text=validated_data['text'])
        note.save()
        return note


class UpdateNoteSerializer(CreateNoteSerializer):

    id = serializers.IntegerField()

    def create(self, validated_data):
        note = Note.objects.get(id=validated_data['id'])
        note.text = validated_data['text']
        note.save()
        return note
