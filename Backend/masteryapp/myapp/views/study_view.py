from rest_framework import viewsets
from rest_framework.viewsets import ViewSet
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

from io import BytesIO
from pdfminer.high_level import extract_text

class StudyView(ViewSet):
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        '''
        Expected format:
        {
            "class",
            "subjects" : [ (can be null)
                string list of specific subjects. If null, a quiz is generated with perceived subject mastery.
            ],
            
        }
        '''
        pass