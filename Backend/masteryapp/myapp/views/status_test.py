# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([])      # Autoriser tout le monde à consulter ce endpoint
def status_view(request):
    print(request.user)
    if request.user.is_authenticated:
        return Response({
            'logged_in': True,
            'username': request.user.username,
            'email': request.user.email,
        }, status=status.HTTP_200_OK)
    else:
        return Response({'logged_in': False}, status=status.HTTP_200_OK)
