from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
import uuid
from django.contrib.auth.models import User


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=300, null=True)
    image_path = models.CharField(max_length=1000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    