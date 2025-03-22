from rest_framework import serializers
from ..models.material_cut import MaterialCut

class MaterialCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCut
        fields = '__all__'