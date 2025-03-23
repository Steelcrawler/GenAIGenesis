from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout, authenticate
from ..serializers.user_signup_serializer import UserSignupSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@authentication_classes([])
@csrf_exempt
def signup_view(request):
    serializer = UserSignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        user.backend = 'myapp.auth_backends.EmailBackend'
        return Response(
            {'detail': f'User created successfully. Welcome, {user}'},
            status=status.HTTP_201_CREATED
        )
    print('Signup errors:', serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
@authentication_classes([])
class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            user.backend = 'myapp.auth_backends.EmailBackend'
            login(request, user)
            return Response(
                {'detail': f'Logged in successfully. Welcome, {user}'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Login failed. Invalid credentials.'},
            status=status.HTTP_404_NOT_FOUND
        )

@authentication_classes([])
class LogoutView(APIView):
    authentication_classes = []  
    permission_classes = []

    def post(self, request, format=None):
        logout(request)
        return Response(
            {'detail': 'Logged out successfully.'},
            status=status.HTTP_200_OK
        )
