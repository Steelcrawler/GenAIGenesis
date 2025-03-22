from rest_framework import serializers
from ..models.class_material import ClassMaterial

class ClassMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassMaterial
        fields = '__all__'