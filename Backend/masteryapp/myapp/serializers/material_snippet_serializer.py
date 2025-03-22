from rest_framework import serializers
from ..models.course import Course
from ..models.material_snippet import MaterialSnippet

class MaterialSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialSnippet
        fields = '__all__'