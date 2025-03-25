from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from reksadana_rest.models import Reksadana
from reksadana_rest.views import create_reksadana, edit_reksadana, get_all_reksadana, get_all_categories, get_all_banks
import requests
import json

# API endpoint
API_BASE_URL = "http://localhost:8001"

def show_dashboard(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({'error': 'Missing Authorization token'}, status=401)
    
    response = requests.get(
                f"{API_BASE_URL}/staff/",
                headers={'Authorization': auth_header}
            )

    if response.status_code == 200:
        return render(request, "dashboard_admin.html",context=get_all_reksadana(request).content)
    else:
        return render("error_page.html", 
                      {'message':'Unauthorized or forbidden access'})
    
@csrf_exempt
def create_uwu(request):
    auth_header = request.headers.get('Authorization')
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
                    return redirect('/staff/daftar_reksadana/')
                else:
                    # TODO
                    error_data = json.loads(create_response.content)
                    return render(request, 'create_reksadana.html', {
                        'error': error_data.get('error', 'Failed to create reksadana'),
                        'categories': get_all_categories(request),
                        'banks': get_all_banks(request)
                    })
            else:
                # TODO
                return JsonResponse({'error': 'Unauthorized or forbidden access'}, status=response.status_code)

        except requests as e:
            # TODO
            return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
    
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
        return JsonResponse({'error': f'Auth service unavailable: {str(e)}'}, status=503)
    

def edit_uwu(request):
    auth_header = request.headers.get('Authorization')
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
                    return redirect('/staff/daftar_reksadana/')
                else:
                    # TODO
                    error_data = json.loads(edit_response.content)
                    return render(request, 'create_reksadana.html', {
                        'error': error_data.get('error', 'Failed to create reksadana'),
                        'categories': get_all_categories(request),
                        'banks': get_all_banks(request)
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

# @csrf_exempt
# def create_reksadana(request):
#     if request.method == 'POST':
#         # Check if user is staff
#         user_role = request.session.get('user_role', None)
#         if user_role != 'user':
#             return render(request, 'create_reksadana.html', {
#                 'error': 'You do not have permission to create reksadana'
#             })

#         try:
#             # Process the form submission
#             create_response = create_reksadana_api(request)
#             if create_response.status_code == 201:  # Created
#                 return redirect('/staff/daftar_reksadana/')
#             else:
#                 error_data = json.loads(create_response.content)
#                 return render(request, 'create_reksadana.html', {
#                     'error': error_data.get('error', 'Failed to create reksadana'),
#                     'categories': get_all_categories(request),
#                     'banks': get_all_banks(request)
#                 })
#         except Exception as e:
#             return render(request, 'create_reksadana.html', {
#                 'error': f'Error: {str(e)}',
#                 'categories': get_all_categories(request),
#                 'banks': get_all_banks(request)
#             })

#     # GET request - show the form
#     try:
#         categories = get_all_categories(request)
#         banks = get_all_banks(request)
#         return render(request, "create_reksadana.html", {
#             'categories': categories,
#             'banks': banks
#         })
#     except Exception as e:
#         return render(request, "create_reksadana.html", {
#             'error': f'Error loading form data: {str(e)}'
#         })
        