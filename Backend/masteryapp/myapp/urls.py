from django.urls import path
from .views.status_test import test_status

urlpatterns = [
    path('status/', test_status, name='status'),
]
