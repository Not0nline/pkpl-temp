from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from reksadana_rest.models import Reksadana
from reksadana_rest.views import create_reksadana, edit_reksadana, get_all_reksadana, get_all_categories, get_all_banks, fetch_all_reksadanas
import requests
import json

# API endpoint
API_BASE_URL = "http://localhost:8001"

def show_dashboard(request):
    auth_header = request.COOKIES.get('jwt_token')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)
    
    response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

    if response.status_code == 200:
        reksadanas = fetch_all_reksadanas()
        context = {
            "reksadanas": reksadanas,
        }
        return render(request, "dashboard_admin.html",context)
    else:
        return render("error_page.html", 
                      {'message':'Unauthorized or forbidden access'})
    
# @csrf_exempt
def create_reksadana_staff(request):
    auth_header = request.COOKIES.get('jwt_token')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)
    
    # POST Create Reksadana
    if request.method == 'POST':
        try:
            response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

            if response.status_code == 200:
                create_response = create_reksadana(request)
                if create_response.status_code == 201:
                    return redirect('/staff/dashboard/')
                else:
                    # TODO
                    error_data = json.loads(create_response.content)
                    return render(request, 'create_reksadana.html', {
                        'error': error_data.get('error', 'Failed to create reksadana'),
                        'categories': get_all_categories(request),
                        'banks': get_all_banks(request)
                    })
            else:
                return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
        except ConnectionError as e:
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
        except Exception as e:
            return JsonResponse({'error': f'{str(e)}'}, status=503)
    
    # Render Create Reksadana Page
    try:
        response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

        if response.status_code == 200:
            categories = get_all_categories(request)
            banks = get_all_banks(request)
            return render(request, "create_reksadana.html", {
                'categories': categories,
                'banks': banks
        })
        else:
            return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
 
    except Exception as e:
        return JsonResponse({'error': f'{str(e)}'}, status=503)
    

def edit_reksadana_staff(request):
    auth_header = request.COOKIES.get('jwt_token')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)
    
    # POST Edit Reksadana
    if request.method == 'POST':
        try:
            response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

            if response.status_code == 200:
                edit_response = edit_reksadana(request)
                if edit_response.status_code == 201:
                    return redirect('/staff/dashboard/')
                else:
                    # TODO
                    reksadana = Reksadana.objects.get(id_reksadana=request.POST.get('reksadana_id'))
                    categories = get_all_categories(request)
                    banks = get_all_banks(request)
                    error_data = json.loads(edit_response.content)
                    return render(request, 'edit_reksadana.html', {
                        'error': error_data.get('error', 'Failed to edit reksadana'),
                        'categories': categories,
                        'banks': banks,
                        'reksadana':reksadana
                    })
            else:
                # TODO
                return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
            
        except requests as e:
            # TODO
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
        
    # Render Edit Reksadana Page
    try:
        response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

        if response.status_code == 200:
            categories = get_all_categories(request)
            banks = get_all_banks(request)
            reksadana = Reksadana.objects.get(id_reksadana=request.GET.get('reksadana_id'))
            return render(request, "edit_reksadana.html", {
                'categories': categories,
                'banks': banks,
                'reksadana':reksadana
        })
        else:
            return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)
 
    except Exception as e:
        return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)