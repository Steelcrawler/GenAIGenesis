from django.urls import path
from .views.status_test import status_view
from .views.auth_view import signup_view, LoginView, LogoutView

urlpatterns = [
    path('status/', status_view, name='status'),
    path('signup/', signup_view, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
