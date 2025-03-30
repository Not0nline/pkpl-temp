from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from reksadana_rest.models import Reksadana
from reksadana_rest.views import create_reksadana, edit_reksadana, get_all_categories, get_all_banks, fetch_all_reksadanas
import requests
import os
import json

# API endpoint
API_BASE_URL = os.environ.get('API_BASE_URL')

def show_dashboard(request):
    auth_header = request.COOKIES.get('jwt_token')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)
    
    try:
        response = requests.get(
                    f"{API_BASE_URL}/staff/",
                    headers={'Authorization': auth_header}
                )

        if response.status_code == 200:
            reksadanas = fetch_all_reksadanas()
            context = {
                "reksadanas": reksadanas,
                'user_role': 'staff'
            }
            return render(request, "dashboard_admin.html",context)
        else:
            return render(request, "error.html", {'error': 'Unauthorized or forbidden access'}) 
    except requests.exceptions.ConnectionError as e:
        return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
    except Exception as e: 
        return JsonResponse({'error': f'{str(e)}'}, status=500) 
        
def create_reksadana_staff(request):
    auth_header = request.COOKIES.get('jwt_token')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/staff/",
            headers={'Authorization': auth_header}
        )
        
        if response.status_code == 200:
            # POST Create Reksadana
            if request.method == 'POST':
                create_response = create_reksadana(request)
                if create_response.status_code == 201:
                    return redirect('/staff/dashboard/')
                else:
                    error_data = json.loads(create_response.content)
                    context = {
                        'error': error_data.get('error', 'Failed to create reksadana'),
                        'categories': get_all_categories(request),
                        'banks': get_all_banks(request),
                        'user_role': 'staff'
                        }  
                    return render(request, 'create_reksadana.html', context)
                    
            # GET Render Create Reksadana Page        
            context = {
                    'categories': get_all_categories(request),
                    'banks': get_all_banks(request),
                    'user_role': 'staff'
                    } 
            return render(request, "create_reksadana.html", context)
                  
        else:
            return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
    except requests.exceptions.ConnectionError as e:
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
    except Exception as e:
        return JsonResponse({'error': f'{str(e)}'}, status=500)
    
def edit_reksadana_staff(request):
    auth_header = request.COOKIES.get('jwt_token')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)

    try:
        response = requests.get(
            f"{API_BASE_URL}/staff/",
            headers={'Authorization': auth_header}
        )
        
        if response.status_code == 200:
            # POST Edit Reksadana
            if request.method == 'POST':
                edit_response = edit_reksadana(request)
                if edit_response.status_code == 201:
                    return redirect('/staff/dashboard/')
                else:
                    error_data = json.loads(edit_response.content)
                    context = {
                        'error': error_data.get('error', 'Failed to edit reksadana'),
                        'reksadana' : Reksadana.objects.get(id_reksadana=request.POST.get('reksadana_id')),
                        'categories': get_all_categories(request),
                        'banks': get_all_banks(request),
                        'user_role': 'staff'
                        }  
                    return render(request, 'edit_reksadana.html', context)
                    
            # GET Render Edit Reksadana Page        
            context = {
                    'reksadana' : Reksadana.objects.get(id_reksadana=request.GET.get('reksadana_id')),
                    'categories': get_all_categories(request),
                    'banks': get_all_banks(request),
                    'user_role': 'staff'
                    } 
            return render(request, "edit_reksadana.html", context)
                  
        else:
            return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
    except requests.exceptions.ConnectionError as e:
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
    except Exception as e:
        return JsonResponse({'error': f'{str(e)}'}, status=500)