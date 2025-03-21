from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def protected_view(request):
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    return JsonResponse({"message": "Hello, user!", "user_id": request.user_id})