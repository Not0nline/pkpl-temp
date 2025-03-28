import json

import requests
import httpx
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from reksadana_rest.views import get_units_by_user,delete_unit_dibeli_by_id
from tibib.utils import *

def index(request):
    if request.method == 'GET':
        try:
            # Debug information
            # print("\n===== PORTFOLIO INDEX DEBUG =====")
            # print("Session contents:", dict(request.session.items()))
            # print("User ID in session:", request.session.get('user_id'))
            # print("User ID as attr:", getattr(request, 'user_id', 'Not set'))
            
            # Ensure user_id is set on request if it's in the session
            if hasattr(request, 'session') and not hasattr(request, 'user_id') and 'user_id' in request.session:
                request.user_id = request.session['user_id']
                # print(f"Manually set user_id on request: {request.user_id}")
            
            # Make sure Authorization header is set if token is in session
            if hasattr(request, 'session') and 'token' in request.session and not request.META.get('HTTP_AUTHORIZATION'):
                request.META['HTTP_AUTHORIZATION'] = request.session['token']
                # print(f"Manually set Authorization header from session token")
            
            # Get portfolio data
            response = get_units_by_user(request)
            
            # Check if the response is an error
            if response.status_code != 200:
                error_data = json.loads(response.content)
                return render(request, 'portfolio.html', context={
                    "error": error_data.get("error", "An error occurred"),
                    "units": [],
                })
            
            # Get success message from session if it exists
            success_message = None
            if request.session and 'success_message' in request.session:
                success_message = request.session['success_message']
                # Remove the message after using it to prevent it from persisting
                del request.session['success_message']
                request.session.modified = True
            data = json.loads(response.content)
            return render(request, 'portfolio.html', context={
                "units": data,
                "success_message": success_message,
            })
        except Exception as e:
            print(f"Error in portfolio index: {str(e)}")
            return render(request, 'portfolio.html', context={
                "error": f"Error loading portfolio: {str(e)}",
                "units": [],
            })
            
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def jual_unitdibeli(request):
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method=='POST':
        #Process jual
        data = request.POST
        id_unitdibeli = data.get("id_unitdibeli")

        base_url = settings.BASE_BACKEND_URL  # Example: "http://127.0.0.1:8000"
        jwt = request.COOKIES.get("jwt_token")
        headers = {
            "Authorization": jwt,  # Add JWT Token here
            "Content-Type": "application/json"
        }

        data = {
            "id_unitdibeli": id_unitdibeli
        }
        
        # return delete_unit_dibeli_by_id(request)
        
        requests.post(
            f"{base_url}/portfolio/process-sell/",  # Full URL
            json=data,
            headers=headers,
        )

        return redirect('/portfolio/')


@csrf_exempt
def process_sell(request):
    if request.method=='POST':
        #Process jual
        delete_unit_dibeli_by_id(request)
        return JsonResponse({"message": "Successfully sold unit reksadana"}, status=201)