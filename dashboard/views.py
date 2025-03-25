import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from reksadana_rest.views import get_all_reksadana, create_unit_dibeli
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


# Create your views here.
def index(request):
    # Check authentication using both request attributes and session
    user_id = getattr(request, 'user_id', None) or request.session.get('user_id')
    if not user_id:
        return redirect('login')
        
    try:
        # Get all reksadana data
        response = get_all_reksadana(request)
        if response.status_code != 200:
            return render(request, "dashboard.html", {
                "error": "Failed to load reksadana data",
                "user_name": request.session.get('nama', 'User')
            })
            
        # Parse response and render dashboard
        data = json.loads(response.content)
        reksadanas = data.get('reksadana', [])
        
        return render(request, "dashboard.html", {
            "reksadanas": reksadanas,
            "user_name": request.session.get('nama', 'User')
        })
    except Exception as e:
        return render(request, "dashboard.html", {
            "error": f"An error occurred: {str(e)}",
            "user_name": request.session.get('nama', 'User')
        })

@csrf_exempt
def beli_unit(request):
    # Check authentication using both request attributes
    user_id = request.user_id
    if not user_id:
        return redirect('login')
        
    if request.method == 'POST':
        try:
            # Handle form submission
            if request.content_type == 'application/json':
                # Handle JSON data (API calls)
                data = json.loads(request.body)
                reksadana_id = data.get("id_reksadana")
                nominal = data.get("nominal")
            else:
                # Handle form data (HTML form)
                reksadana_id = request.POST.get("id_reksadana")
                nominal = request.POST.get("nominal")

            # Validate required fields
            if not reksadana_id or not nominal:
                return render(request, "error.html", {
                    "error": "Missing required fields",
                    "back_url": "/"
                })
                
            try:
                nominal = float(nominal)
                if nominal < 10000:  # Minimum investment amount
                    return render(request, "error.html", {
                        "error": "Minimum investment amount is Rp 10,000",
                        "back_url": "/"
                    })
            except ValueError:
                return render(request, "error.html", {
                    "error": "Invalid amount format",
                    "back_url": "/"
                })
            
            # Process payment
            return render(request, "payment_confirmation.html", {
                "reksadana_id": reksadana_id,
                "nominal": nominal,
                "user_id": user_id
            })
        except Exception as e:
            return render(request, "error.html", {
                "error": f"An error occurred: {str(e)}",
                "back_url": "/"
            })
    
    # GET request - redirect to dashboard
    return redirect('index')

# async function call
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        try:
            if not request.user_id:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = {
                    'user_id': request.session.get('user_id'),
                    'id_reksadana': request.POST.get('id_reksadana'),
                    'nominal': request.POST.get('nominal'),
                    'payment_method': request.POST.get('payment_method'),
                }

            if not data.get('id_reksadana') or not data.get('nominal'):
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            try:
                # Try to handle various formats including commas and currency symbols
                nominal_str = str(data.get('nominal')).replace('Rp', '').replace(',', '').replace('.', '').strip()
                nominal_int = int(nominal_str)
            except ValueError as e:
                print(f"Value error when converting nominal: {e}")
                return render(request, "error.html", {
                    "error": f"Invalid amount format: {data.get('nominal')}",
                    "back_url": "/"
                })
            
            # Also prepare the JSON body for the API functions
            request._body = json.dumps({
                'id_reksadana': data.get('id_reksadana'),
                'nominal': encode_value(nominal_int),
            }).encode('utf-8')

            # Create unit dibeli
            res = create_unit_dibeli(request)
            if res.status_code != 201:
                error_data = json.loads(res.content.decode('utf-8'))
                return render(request, "error.html", {
                    "error": f"Unit creation failed: {error_data.get('error', 'Unknown error')}",
                    "back_url": "/"
                })

            # Store success message in session for display on next page
            request.session['success_message'] = "Your investment has been processed successfully!"
            
            # Redirect to portfolio page instead of dashboard
            return redirect('/portfolio/')
            
        except Exception as e:
            print(f"Exception in process_payment: {str(e)}")
            return render(request, "error.html", {
                "error": f"An error occurred: {str(e)}",
                "back_url": "/"
            })

    return HttpResponse("Method not allowed", status=405)