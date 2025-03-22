from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
import uuid
from .class_material import ClassMaterial
from .subject import Subject

class MaterialSnippet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_material = models.ForeignKey(ClassMaterial, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    snippet = models.CharField(max_length=5000)
    
    
    