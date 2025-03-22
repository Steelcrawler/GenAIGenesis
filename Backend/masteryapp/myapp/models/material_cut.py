from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from .course import Course
import uuid
from .class_material import ClassMaterial
from .subcategory import Subcategory

class MaterialCut(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_material = models.ForeignKey(ClassMaterial, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)
    cut_start = models.PositiveIntegerField()
    cut_end = models.PositiveIntegerField()
    
    
    