from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models.course import Course
from ..models.material_snippet import MaterialSnippet
from ..serializers.course_serializer import CourseSerializer
from ..auth_backends import CsrfExemptSessionAuthentication
from rest_framework.authentication import BasicAuthentication
from ..serializers.material_snippet_serializer import MaterialSnippetSerializer


class MaterialSnippetViewset(viewsets.ModelViewSet):
    serializer_class = MaterialSnippetSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = MaterialSnippet.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MaterialSnippetSerializer.objects.filter(class_material__course__user=self.request.user)
        return MaterialSnippet.objects.none()

    def get(self, request, *args, **kwargs):
        id_param = kwargs.get('pk')
        if id_param:
            try:
                client = MaterialSnippet.objects.get(pk=id_param)
                serializer = self.get_serializer(client)
                return Response({
                    'material_snippet' : serializer.data
                },
                                status=status.HTTP_200_OK)
            except MaterialSnippet.DoesNotExist:
                return Response({"error": "Snippet not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'material_snippets' : serializer.data
            },
                            status=status.HTTP_200_OK)
            
    
    
        