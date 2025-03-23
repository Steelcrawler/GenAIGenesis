from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models.course import Course
from ..serializers.course_serializer import CourseSerializer
from ..auth_backends import CsrfExemptSessionAuthentication
from rest_framework.authentication import BasicAuthentication



class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Course.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Course.objects.filter(user=self.request.user)
        return Course.objects.none()

    
    def retrieve(self, request, *args, **kwargs):
        id_param = kwargs.get('pk')
        try:
            course = Course.objects.get(pk=id_param)
            serializer = self.get_serializer(course)
            return Response({'course': serializer.data}, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)


    def list(self, request, *args, **kwargs):
        queryset = Course.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'courses': serializer.data}, status=status.HTTP_200_OK)

            


    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = self.request.user.id
        serializer = CourseSerializer(data=data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response({
                'error' : serializer.errors
            },
                            status=status.HTTP_400_BAD_REQUEST)
            
        new_course = serializer.save()
        return Response({
            'course' : CourseSerializer(new_course).data
        },
                        status=status.HTTP_201_CREATED)
        
    
    def update(self, request, *args, **kwargs):
        id_param = kwargs.get('pk')
        if not id_param: 
            return Response({'error': 'Missing required field: id'}, status=status.HTTP_400_BAD_REQUEST)
        
        try: 
            course = Course.objects.get(pk=id_param)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        serializer = CourseSerializer(course, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'error' : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        course = serializer.save()
        return Response({
            'course' : CourseSerializer(course).data
        },
                        status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        id_param = kwargs.get('pk')
        if not id_param:
            return Response({'error': 'Missing required field: id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(pk=id_param)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        course.delete()

        return Response({'message': 'Course deleted successfully'}, status=status.HTTP_200_OK)
    
    
    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='add_material')
    def add_material(self, request, pk=None):
        course = get_object_or_404(Course, pk=pk)
    
        # Get material data
        material_data = request.data.copy()
        material_data['course'] = pk  # Set course ID
        
        # Create material using the appropriate serializer
        from ..serializers.class_material_serializer import ClassMaterialSerializer
        serializer = ClassMaterialSerializer(data=material_data)
        
        if serializer.is_valid():
            material = serializer.save()
            return Response({
                'class_material': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        