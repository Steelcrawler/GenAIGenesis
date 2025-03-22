from django.urls import path, include
from .views.status_test import status_view
from .views.auth_view import signup_view, LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from .views.course_view import CourseViewSet
from .views.class_material_view import ClassMaterialViewSet
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'materials', ClassMaterialViewSet, basename='class_material')


urlpatterns = [
    path('', include(router.urls)),
    path('status/', status_view, name='status'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
