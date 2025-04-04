import json
from rest_framework import viewsets

from ..serializers.material_snippet_serializer import MaterialSnippetSerializer

from ..serializers.class_material_serializer import ClassMaterialSerializer
from ..serializers.subject_serializer import SubjectSerializer
from ..models.class_material import ClassMaterial
from ..serializers.class_material_serializer import ClassMaterialSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..gcp.uploadpdf import upload_process_and_highlight_pdf
from ..models.course import Course
from ..models.subject import Subject
from ..models.material_snippet import MaterialSnippet
from ..serializers.course_serializer import CourseSerializer
from ..serializers.material_snippet_serializer import MaterialSnippetSerializer
from ..auth_backends import CsrfExemptSessionAuthentication
from rest_framework.authentication import BasicAuthentication
from ..gcp.gc_utils import get_pdf_bytes_from_gcs
import base64


from io import BytesIO

class ClassMaterialViewSet(viewsets.ModelViewSet):
    queryset = ClassMaterial.objects.all()
    serializer_class = ClassMaterialSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        class_material = get_object_or_404(ClassMaterial, pk=pk)
        print('class_material: ', class_material.course.id)
        print('user_id: ', request.user.id)
        print('blob_name: ', class_material.file_name.split('/').pop())
        file_bytes = get_pdf_bytes_from_gcs(
            bucket_name="educatorgenai",
            user_id=request.user.id,
            course_id=class_material.course.id,
            file_name=class_material.file_name.split('/').pop(),
        )
        encoded_file = base64.b64encode(file_bytes).decode('utf-8')
        print('Received detailed request, sending data: ')
        return Response({
            'class_material' : ClassMaterialSerializer(class_material).data,
            'file' : encoded_file
        },
                        status=status.HTTP_200_OK)
    

    def list(self, request, *args, **kwargs):
        course_id = self.request.query_params.get('course_id')
        
        if course_id:
            queryset = ClassMaterial.objects.filter(course__id=course_id)
        else:
            queryset = ClassMaterial.objects.filter(course__user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'class_materials': serializer.data
        }, status=status.HTTP_200_OK)
                 
        
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print('request.data: ', request.data)
        data = request.data
        print('data: ', data)

        material_raw = json.loads(data['material'])

        print('material_raw: ', material_raw)
        course_id = data['course_id']
        
        pdf_file = request.FILES.get('file')
        
        existing_subjects_qs = Subject.objects.filter(course__id=course_id)
        existing_subjects = {str(subcat.name.lower()): subcat for subcat in existing_subjects_qs}
        print('user_id: ', str(request.user.id))
        parse_result = upload_process_and_highlight_pdf(file_obj=pdf_file, 
                                              bucket_name="educatorgenai", 
                                              user_id=str(request.user.id),
                                              credentials_path='genaigenesis-454500-2b74084564ba.json',
                                              file_name=material_raw['file_name'],
                                              course_id=course_id,
                                              )
        
        print('parse_result: ', parse_result)
        success = parse_result.get('success', False)
        
        if not success:
            return Response({
                'error' : 'Parse method failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        all_subjects = parse_result['subjects']
        
        for subject in all_subjects:
            subject_name = subject['subject']
            if not subject_name.lower() in existing_subjects.keys():
                new_subject = Subject.objects.create(
                    name=subject_name,
                    course_id=course_id
                )
                existing_subjects[subject_name.lower()] = new_subject
            
        all_partitions = parse_result['text_partitions']
        
        # By now, creating a class_material is required.
        new_material = ClassMaterial.objects.create(
            file_name=parse_result["pdf_name"],
            custom_name=material_raw.get('custom_name', None),
            course_id=course_id,
            weight=material_raw.get('weight', 1),
        )
        
        for item in all_partitions:
            print('item: ', item)
            target_subject = item['subject']
            snippet = item['text']
            if not target_subject.lower() in existing_subjects.keys():
                return Response({
                    'error' : 'Internal parse suggested inexisting subject.'
                },
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            new_snippet = MaterialSnippet.objects.create(
                class_material=new_material,
                subject=existing_subjects[target_subject.lower()],
                snippet=snippet
            )
            
        final_snippets = MaterialSnippet.objects.filter(class_material=new_material)
        final_subjects = Subject.objects.filter(course_id=course_id)
            
        return Response({
            'class_material' : ClassMaterialSerializer(new_material).data,
            'subjects' : SubjectSerializer(final_subjects, many=True, context={'request': request}).data,
            'material_snippets' : MaterialSnippetSerializer(final_snippets, many=True).data,
        }, status=status.HTTP_201_CREATED)