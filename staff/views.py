from django.shortcuts import redirect, render
from reksadana_rest.views import *
import requests

# API endpoint
API_BASE_URL = "http://localhost:8001"

def daftar_reksadana(request):
    return render(request, "daftar_reksadana.html",context=get_all_reksadana(request).content)
    
@csrf_exempt
def create_uwu(request):
    if request.method == 'POST':
        # Make a call to the auth microservice
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Missing Authorization token'}, status=401)

        try:
            response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

            if response.status_code == 200:
                create_reksadana(request)
                return redirect('/staff/daftar_reksadana/')
            else:
                return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)

        except requests.RequestException as e:
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)

    return render(request, "create_reksadana.html", context={})

def edit_uwu(request):
    if request.method == 'POST':
        # Make a call to the auth microservice
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({'error': 'Missing Authorization token'}, status=401)
        try:
            response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

            if response.status_code == 200:
                edit_reksadana(request)
                return redirect('/staff/daftar_reksadana/')
            else:
                return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
            
        except requests.RequestException as e:
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
        
    return render(request, "edit_reksadana.html", context={})
