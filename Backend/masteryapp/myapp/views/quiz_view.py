from rest_framework import viewsets

from masteryapp.myapp.serializers.material_snippet_serializer import MaterialSnippetSerializer
from masteryapp.myapp.serializers.subject_serializer import SubjectSerializer
from ..models.class_material import ClassMaterial
from ..serializers.class_material_serializer import ClassMaterialSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import requests
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404

from ..models.course import Course
from ..models.subject import Subject
from ..models.material_snippet import MaterialSnippet
from ..serializers.course_serializer import CourseSerializer
from ..serializers.quiz_serializer import QuizSerializer
from ..models.quiz import Quiz
from ..models.material_snippet import MaterialSnippet

from io import BytesIO
from pdfminer.high_level import extract_text

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if pk:
            class_material = get_object_or_404(Quiz, pk=pk)
            return Response({
                'quiz' : QuizSerializer(class_material).data
            },
                            status=status.HTTP_200_OK)
            
        course_id = self.request.query_params.get('course_id')
        
        if course_id:
            queryset = Quiz.objects.filter(course_id=course_id)
        else:
            queryset = Quiz.objects.filter(user=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'quizzes': serializer.data
        }, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = QuizSerializer(data=data)
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
        
        
        
            
