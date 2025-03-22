from django.urls import path, include
from .views.status_test import test_status
from rest_framework.routers import DefaultRouter
from .views.course_view import CourseViewSet
from .views.class_material_view import ClassMaterialViewSet
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'materials', ClassMaterialViewSet, basename='class_material')


urlpatterns = [
    path('', include(router.urls)),
    path('status/', test_status, name='status'),
]
