from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from .course import Course
from .subject import Subject
from .material_snippet import MaterialSnippet
import uuid
from django.contrib.auth.models import User

class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    subjects = models.ManyToManyField(Subject, blank=True)
    materials = models.ManyToManyField(MaterialSnippet, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    optimize_learning = models.BooleanField(default=True)
    quiz_length = models.SmallIntegerField(default=20)
    options_per_question = models.SmallIntegerField(defaut=4)
    