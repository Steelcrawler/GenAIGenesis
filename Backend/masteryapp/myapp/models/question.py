from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from .quiz import Quiz
import uuid
from django.contrib.auth.models import User
from .subcategory import Subcategory

class QuestionType(models.TextChoices):
    SHORT_ANSWER = 'SHORT_ANSWER', 'Short answer'
    MULTIPLE_ANSWER = 'MULTIPLE_ANSWER', 'Multiple answer'
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'Multiple choice'

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=3000)
    type = models.CharField(
        max_length=25,
        choices=QuestionType.choices,
    )
    choices = models.CharField(max_length=10000, null=True) # Separated by ';;/;;' per different question to store as a string.
    correct_choices = models.CharField(max_length=100, null=True) # The index(es) of the correct answer.
    correct_short_answer = models.CharField(max_length=3000,null=True)
    attempted_choices = models.CharField(max_length=100, null=True)
    attempted_short_answer = models.CharField(max_length=3000, null=True)
    is_correct = models.BooleanField(null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True)
    
    