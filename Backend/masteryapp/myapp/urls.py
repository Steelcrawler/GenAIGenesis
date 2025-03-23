from django.urls import path, include
from .views.status_test import status_view
from .views.auth_view import signup_view, LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from .views.course_view import CourseViewSet
from .views.class_material_view import ClassMaterialViewSet
from .views.material_snippet_view import MaterialSnippetViewset
from .views.question_view import QuestionViewset
from .views.quiz_view import QuizViewSet
from .views.subject_view import SubjectViewset
router = DefaultRouter()

router.register(r'materials', ClassMaterialViewSet, basename='class_material')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'snippets', MaterialSnippetViewset, basename='snippet')
router.register(r'questions', QuestionViewset, basename='question')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'subjects', SubjectViewset, basename='subject')


urlpatterns = [
    path('', include(router.urls)),
    path('status/', status_view, name='status'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
