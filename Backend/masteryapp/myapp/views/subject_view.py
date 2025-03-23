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
from ..models.subject import Subject
from ..models.question import Question
from ..serializers.subject_serializer import SubjectSerializer
from ..models.material_snippet import MaterialSnippet

from io import BytesIO
from pdfminer.high_level import extract_text
from ..gcp.rag_question_maker import QuizMakerRAG

class SubjectViewset(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    
    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        subject = get_object_or_404(Subject, pk=pk)
        serializer = self.get_serializer(subject)
        return Response({'subject': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        course_id = request.query_params.get('course_id')
        if course_id:
            queryset = Subject.objects.filter(course_id=course_id)
        else:
            queryset = Subject.objects.filter(course__user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'subjects': serializer.data}, status=status.HTTP_200_OK)



            
