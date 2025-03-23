import json
import random
from rest_framework import viewsets
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
from ..models.question import Question
from ..serializers.question_serializer import QuestionSerializer
from ..models.material_snippet import MaterialSnippet

from io import BytesIO
from pdfminer.high_level import extract_text
from ..gcp.rag_question_maker import QuizMakerRAG

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            question = get_object_or_404(Question, pk=pk)
            return Response({
                'question' : Question(question).data
            },
                            status=status.HTTP_200_OK)
            
        quiz_id = self.request.query_params.get('quiz_id')
        
        if quiz_id:
            queryset = Question.objects.filter(quiz_id=quiz_id)
        else:
            queryset = Question.objects.filter(quiz__user=self.request.user)
        serializer = self.get_serializer(queryset, manyr=True)
        return Response({
            'questions': serializer.data
        }, status=status.HTTP_200_OK)
    


            
