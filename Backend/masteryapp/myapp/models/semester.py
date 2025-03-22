from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from .course import Course
import uuid

class Semester(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)