from django.utils import timezone
from rest_framework import serializers
from ..models.subject import Subject
from ..models.question import Question
from ..models.material_snippet import MaterialSnippet

MAX_SNIPPET_MASTERY = 7

class SubjectSerializer(serializers.ModelSerializer):
    mastery = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = '__all__'
        
    def get_mastery(self, obj):
        user = self.context['request'].user  
        return compute_category_mastery(obj, user)

    

def compute_snippet_mastery(snippet, user):
    """
    Compute the mastery score for a given snippet for the user.
    For each answered question related to the snippet:
      - Add +1 (multiplied by a decay factor) for a correct answer.
      - Subtract -1 (multiplied by the decay factor) for a wrong answer.
    The decay factor is calculated based on how many days have passed since the quiz was completed,
    so older questions contribute less.
    The final snippet mastery is clamped between 0 and MAX_SNIPPET_MASTERY.
    """
    # Retrieve questions for this snippet where the quiz is completed.
    questions = Question.objects.filter(
        quiz__user=user,
        snippet=snippet,
        quiz__completed_at__isnull=False
    )
    
    mastery = 0.0
    now = timezone.now()
    
    for question in questions:
        # Calculate decay factor: decay decreases 1% per day
        days_since = (now - question.quiz.completed_at).days
        decay = max(0, 1 - (0.01 * days_since))
        
        if question.is_correct:
            mastery += decay
        else:
            mastery -= decay

    # Clamp mastery between 0 (min) and MAX_SNIPPET_MASTERY (max)
    mastery = max(0, min(mastery, MAX_SNIPPET_MASTERY))
    return mastery


def compute_category_mastery(subject, user):
    """
    Compute the overall mastery for a category (subject) by:
      - Finding all snippets belonging to the subject.
      - Calculating each snippet's mastery.
      - Returning the average mastery score across those snippets.
    """
    snippets = MaterialSnippet.objects.filter(subject=subject)
    if not snippets.exists():
        return 0  # Or return None or an appropriate value when no snippets exist.

    total_mastery = 0.0
    count = 0
    for snippet in snippets:
        snippet_mastery = compute_snippet_mastery(snippet, user)
        total_mastery += snippet_mastery
        count += 1

    category_mastery = total_mastery / count if count > 0 else 0
    return category_mastery