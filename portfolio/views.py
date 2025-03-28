import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from django.contrib import messages
import requests
import httpx
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from reksadana_rest.views import get_units_by_user,delete_unit_dibeli_by_id
import os
import base64

AES_KEY = base64.b64decode(os.getenv("AES_KEY"))
AES_IV = base64.b64decode(os.getenv("AES_IV"))

def encode_value(value):
    """
    Encrypts a single value using AES.
    """
    padder = padding.PKCS7(128).padder()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(AES_IV), backend=default_backend())
    encryptor = cipher.encryptor()

    # Convert value to string and pad it
    value_str = str(value)
    padded_data = padder.update(value_str.encode('utf-8')) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data.hex()  # Convert bytes to hex string

# TODO: Not tested with postman
def index(request):
    if request.method == 'GET':
        try:
            # Debug information
            # print("\n===== PORTFOLIO INDEX DEBUG =====")
            # print("Session contents:", dict(request.session.items()))
            # print("User ID in session:", request.session.get('user_id'))
            # print("User ID as attr:", getattr(request, 'user_id', 'Not set'))
            
            # Ensure user_id is set on request if it's in the session
            if not hasattr(request, 'user_id') and 'user_id' in request.session:
                request.user_id = request.session['user_id']
                # print(f"Manually set user_id on request: {request.user_id}")
            
            # Make sure Authorization header is set if token is in session
            if 'token' in request.session and not request.META.get('HTTP_AUTHORIZATION'):
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
                    "user_name": request.session.get('nama', 'User')
                })
            
            # Get success message from session if it exists
            success_message = None
            if 'success_message' in request.session:
                success_message = request.session['success_message']
                # Remove the message after using it to prevent it from persisting
                del request.session['success_message']
                request.session.modified = True
                
            data = json.loads(response.content)
            return render(request, 'portfolio.html', context={
                "units": data,
                "success_message": success_message,
                "user_name": request.session.get('nama', 'User')
            })
        except Exception as e:
            print(f"Error in portfolio index: {str(e)}")
            return render(request, 'portfolio.html', context={
                "error": f"Error loading portfolio: {str(e)}",
                "units": [],
                "user_name": request.session.get('nama', 'User')
            })
            
    return JsonResponse({"error": "Invalid request method"}, status=405)

# TODO: Not tested with postman
# @csrf_exempt
def jual_unitdibeli(request):
    """
    Process selling a unit
    """
    # Ensure user is authenticated
    if not request.user_id:
        messages.error(request, "Unauthorized access")
        return redirect('login')

    if request.method == 'POST':
        # Get the unit ID to sell
        id_unitdibeli = request.POST.get("id_unitdibeli")
        
        if not id_unitdibeli:
            messages.error(request, "Missing unit ID")
            return redirect('/portfolio/')

        try:
            # Prepare request body
            request._body = json.dumps({
                "id_unitdibeli": id_unitdibeli
            }).encode('utf-8')

            # Call delete function
            response = delete_unit_dibeli_by_id(request)

            # Check response status
            if response.status_code == 201:
                messages.success(request, "Successfully sold unit reksadana")
            else:
                # Parse error message if available
                try:
                    error_data = json.loads(response.content.decode('utf-8'))
                    messages.error(request, error_data.get('error', 'Failed to sell unit'))
                except:
                    messages.error(request, 'Failed to sell unit')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('/portfolio/')

    # Handle non-POST requests
    messages.error(request, "Invalid request method")
    return redirect('/portfolio/')


# @csrf_exempt
def process_sell(request):
    """
    Validate and process the sell request
    """
    # Ensure user is authenticated
    if not request.user_id:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method == 'POST':
        try:
            # Call delete function
            response = delete_unit_dibeli_by_id(request)

            # Check response status
            if response.status_code == 201:
                return JsonResponse({"message": "Successfully sold unit reksadana"}, status=201)
            else:
                # Parse error message if available
                try:
                    error_data = json.loads(response.content.decode('utf-8'))
                    return JsonResponse({"error": error_data.get('error', 'Failed to sell unit')}, status=400)
                except:
                    return JsonResponse({"error": "Failed to sell unit"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)