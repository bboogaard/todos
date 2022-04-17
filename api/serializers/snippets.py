from rest_framework import serializers

from api.data.models import CodeSnippet


class ListCodeSnippetSerializer(serializers.ModelSerializer):

    class Meta:
        model = CodeSnippet
        fields = ['id', 'text']


class CreateCodeSnippetSerializer(serializers.Serializer):

    text = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        snippet = CodeSnippet(text=validated_data['text'])
        snippet.save()
        return snippet


class UpdateCodeSnippetSerializer(CreateCodeSnippetSerializer):

    id = serializers.IntegerField()

    def create(self, validated_data):
        snippet = CodeSnippet.objects.get(id=validated_data['id'])
        snippet.text = validated_data['text']
        snippet.save()
        return snippet
