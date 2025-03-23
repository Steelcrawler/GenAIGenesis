import json
import random
from rest_framework import viewsets

from myapp.auth_backends import CsrfExemptSessionAuthentication
from ..models.class_material import ClassMaterial
from ..serializers.class_material_serializer import ClassMaterialSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import requests
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from vertexai.preview.generative_models import GenerativeModel
from django.db import transaction
        
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models.course import Course
from ..models.subject import Subject
from ..models.question import Question, QuestionType
from ..models.material_snippet import MaterialSnippet
from ..serializers.course_serializer import CourseSerializer
from ..serializers.question_serializer import QuestionSerializer
from ..serializers.quiz_serializer import QuizSerializer
from ..models.quiz import Quiz
from rest_framework.authentication import BasicAuthentication
from ..models.material_snippet import MaterialSnippet

from io import BytesIO
from pdfminer.high_level import extract_text
from ..gcp.rag_question_maker import QuizMakerRAG

MAX_SNIPPET_MASTERY = 7

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = self.get_serializer(quiz)
        return Response({'quiz': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id')
        if course_id:
            queryset = Quiz.objects.filter(course_id=course_id)
        else:
            queryset = Quiz.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'quizzes': serializer.data}, status=status.HTTP_200_OK)

    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        now = timezone.now()
        human_date = now.strftime("%d %B")
        data['name'] = data.get('name', f'{human_date} quiz')
        serializer = QuizSerializer(data=data)
        print(f"QuizView Create data: {data}")
        if not serializer.is_valid():
            return Response({
                'error' : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        new_quiz: Quiz = serializer.save()
        
        if new_quiz.subjects.exists():
            source_snippets = MaterialSnippet.objects.filter(
                subject__course=new_quiz.course,
                subject__in=new_quiz.subjects.all()
            )
            new_quiz.optimize_learning = False
            new_quiz.save()
            # If going by subject, there's no point checking the mastery of said subject or doing any comparing.
        elif new_quiz.materials.exists():
            source_snippets = MaterialSnippet.objects.filter(
                class_material__in = new_quiz.materials.all()
            )
        else:
            source_snippets = MaterialSnippet.objects.filter(
                subject__course=new_quiz.course
            )
        
        # By now we have the source snippets.
        
        weighted_snippets = []
        for snippet in source_snippets:
            subject = snippet.subject
            mastery = self.compute_mastery_score(subject, request.user)
            weight = self.compute_weight(mastery)
            weighted_snippets.append((snippet, weight))

        selected_snippets = random.choices(
            population=[snip for snip, wt in weighted_snippets],
            weights=[wt for snip, wt in weighted_snippets],
            k=new_quiz.quiz_length
        )
        
        data_list = []
        counter = 0
        for snippet in selected_snippets:
            counter+=1
            data_list.append({
                'id' : str(snippet.id),
                'snippet' : str(snippet.snippet),
                'commented_count_helper': counter,
            })
        
        quiz_maker_rag = QuizMakerRAG()
        corpus_name = quiz_maker_rag.setup_corpus(
            bucket_name="educatorgenai",
            data_list=data_list
        )
        model: GenerativeModel = quiz_maker_rag.setup_model(corpus_name=corpus_name)
        model_response = quiz_maker_rag.generate_response(
            query="",
            model=model,
            quiz_length=len(selected_snippets),
            options_per_question=new_quiz.options_per_question,
        )
        try:
            parsed_model_response = json.loads(model_response)
        except Exception as e:
            return Response(
                {
                    'error' : f'Parse error of generative models response: {e}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        for question_raw in parsed_model_response:
            new_question = Question.objects.create(
                quiz_id=new_quiz.id,
                question=question_raw['question'],
                choices=';;/;;'.join(question_raw['choices']),
                type=QuestionType.MULTIPLE_CHOICE.value, # Hard-coded for now.
                single_correct_choice=question_raw['answer_index'],
                snippet_id=question_raw['snippet_id'],
            )
            
        final_questions = Question.objects.filter(quiz=new_quiz)
        
        return Response({
            'quiz' : QuizSerializer(new_quiz).data,
            'questions' : QuestionSerializer(final_questions, many=True).data
        },
                        status=status.HTTP_201_CREATED)
        
        
    @transaction.atomic
    @action(detail=True, methods=['patch'], url_path='submit')
    def submit(self, request, pk=None):
        if pk is None:
            return Response({
                'error' : 'Tried to submit a quiz without providing quiz ID'
            }, status=status.HTTP_400_BAD_REQUEST) # status.DUMBASS
        
        target_quiz: Quiz = get_object_or_404(Quiz, pk=pk)
        
        data = self.data.copy()
        
        submitted_questions = data.get('questions')
        
        if submitted_questions is None:
            return Response({
                'error' : 'Cannot submit quiz without providing related question.s final form.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        quiz_questions = Question.objects.filter(quiz=target_quiz).all()
        quiz_questions_dict = {question.id: question for question in quiz_questions}
        
        if len(submitted_questions) != len(quiz_questions):
            return Response({
                'error' : 'Submitted questions length do not match quiz question length.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        for submit_question in submitted_questions:
            #TODO : More than just multiple answer questions!
            attempted_answer = submit_question['single_choice']
            question: Question = quiz_questions_dict[submit_question['id']]
            question.is_correct = int(attempted_answer) == question.single_correct_choice
            question.save()
        
        target_quiz.completed_at = timezone.now()
        target_quiz.save()
        
        final_questions = Question.objects.filter(quiz=target_quiz)
        
        return Response({
            'quiz' : QuizSerializer(target_quiz).data,
            'questions' : QuestionSerializer(final_questions, many=True)
        }, status=status.HTTP_200_OK)
            
        
        
    def compute_mastery_score(self, subject, user):
        # Retrieve questions for this user and subject.
        questions = Question.objects.filter(quiz__user=user, snippet__subject=subject)
        mastery = 0.0
        now = timezone.now()
        
        for question in questions:
            if question.is_correct is None:
                continue # Unanswered question
            # If question is answered, it's quiz has a completed_at date.
            days_since = (now - question.quiz.completed_at).days
            degradation = max(0, 1 - (0.01 * days_since))
            if question.is_correct:
                mastery += degradation
            else:
                mastery -= degradation
        return mastery
    
    def compute_weight(self, mastery):
        # but if mastery is negative, we further add the weight: weight = 1 + abs(mastery).
        # maybe the weighing is to be reworked.
        if mastery >= 0:
            return 1 / (1 + mastery)
        else:
            return 1 + abs(mastery)


            
