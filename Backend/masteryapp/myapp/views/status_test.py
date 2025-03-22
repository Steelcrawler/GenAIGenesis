from django.http import JsonResponse

def test_status(request):
    return JsonResponse({"status": "Server is running..."})
