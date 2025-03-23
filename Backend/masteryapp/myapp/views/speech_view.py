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
from ..models.class_material import ClassMaterial
from ..models.material_snippet import MaterialSnippet
from ..serializers.course_serializer import CourseSerializer
from ..gcp.stt_generator import get_command_from_bytes
from ..gcp.tts_generator import text_to_speech_bytes
from io import BytesIO
from pdfminer.high_level import extract_text

class SpeechView(ViewSet):
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path='send_instruction')
    def send_instruction(self, request):
        audio_bytes = request.FILES.get('audio')
        all_courses = Course.objects.filter(user=request.user).all()
        all_material = ClassMaterial.objects.filter(course__user = request.user).all()
        all_courses_dict = {course.name: course for course in all_courses}
        all_material_dict = {material.file_name: material for material in all_material}
        
        #TODO: Call function here.
        interpretation_dict = get_command_from_bytes(
            audio_bytes=audio_bytes,
            course_names=all_courses_dict.keys(),
            pdf_names=all_material_dict.keys()
        )
        inferred_action = interpretation_dict['action']
        # Only these options require mentioning a course and/or a material.
        if inferred_action in ('Open', ):
            inferred_course = interpretation_dict['course_name']
            inferred_material = interpretation_dict['pdf_name']
            if inferred_course not in all_courses_dict or inferred_material not in all_material_dict:
                return Response({
                    'error' : 'Inferred inexisting course or material from audio'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({
                'action' : inferred_action,
                'course' : CourseSerializer(all_courses_dict[inferred_course]).data,
                'material' : ClassMaterialSerializer(all_material_dict[inferred_material]).data,
            })
        return Response({
            'action' : inferred_action
        })
        
    @action(detail=False, methods=['post'], url_path='receive_speech_bytes')        
    def receive_speech_bytes(self, request):
        data = request.data.copy()
        text_to_parse = data['text']
        audio_bytes = text_to_speech_bytes(
            text=text_to_parse
        )
        return Response({
            'audio_bytes' : audio_bytes
        }, status=status.HTTP_200_OK)