from django.shortcuts import redirect, render
from reksadana_rest.views import *
import requests
import json

# API endpoint
API_BASE_URL = "http://localhost:8001"

def daftar_reksadana(request):
    return render(request, "daftar_reksadana.html",context=get_all_reksadana(request).content)
    
@csrf_exempt
def create_reksadana(request):
    if request.method == 'POST':
        # Check if user is staff
        user_role = request.session.get('user_role', None)
        if user_role != 'user':
            return render(request, 'create_reksadana.html', {
                'error': 'You do not have permission to create reksadana'
            })

        try:
            # Process the form submission
            create_response = create_reksadana_api(request)
            if create_response.status_code == 201:  # Created
                return redirect('/staff/daftar_reksadana/')
            else:
                error_data = json.loads(create_response.content)
                return render(request, 'create_reksadana.html', {
                    'error': error_data.get('error', 'Failed to create reksadana'),
                    'categories': get_all_categories(request),
                    'banks': get_all_banks(request)
                })
        except Exception as e:
            return render(request, 'create_reksadana.html', {
                'error': f'Error: {str(e)}',
                'categories': get_all_categories(request),
                'banks': get_all_banks(request)
            })

    # GET request - show the form
    try:
        categories = get_all_categories(request)
        banks = get_all_banks(request)
        return render(request, "create_reksadana.html", {
            'categories': categories,
            'banks': banks
        })
    except Exception as e:
        return render(request, "create_reksadana.html", {
            'error': f'Error loading form data: {str(e)}'
        })

def edit_reksadana(request):
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
