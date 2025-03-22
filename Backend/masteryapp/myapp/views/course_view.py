from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404

from ..models.course import Course
from ..serializers.course_serializer import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        id_param = kwargs.get('pk')
        if id_param:
            try:
                client = Course.objects.get(pk=id_param)
                serializer = self.get_serializer(client)
                return Response({
                    'course' : serializer.data
                },
                                status=status.HTTP_200_OK)
            except Course.DoesNotExist:
                return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            queryset = Course.objects.filter(user=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'courses' : serializer.data
            },
                            status=status.HTTP_200_OK)
            


    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = self.request.user.id
        serializer = CourseSerializer(data=data)
        if not serializer.is_valid():
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
        serializer = Course(course, data=data, partial=True)
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
        course: Course = get_object_or_404(Course, pk=pk)
        data = request.data.copy()
        material_data = data['material']
        