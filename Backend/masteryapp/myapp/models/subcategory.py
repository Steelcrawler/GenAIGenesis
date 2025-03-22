from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from .course import Course
import uuid

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="material"
    )
    
    
    