from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from .course import Course
import uuid

class ClassMaterial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=500)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="material"
    )
    weight = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(20)],
        null=True
    )
    
    