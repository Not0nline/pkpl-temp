import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from reksadana_rest.views import get_all_reksadana, create_unit_dibeli, create_payment
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
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    reksadanas = json.loads(get_all_reksadana(request).content)['reksadana']
    #TODO: Bikin html dashboard
    return render(request, "dashboard.html", context=reksadanas)

@csrf_exempt
def beli_unit(request):
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method=='POST':
        #Simulate third party payment
        data = json.loads(request.body)
        reksadana_id = data.get("id_reksadana")
        nominal = data.get("nominal")
        
        base_url = settings.BASE_BACKEND_URL  # Example: "http://127.0.0.1:8000"
        jwt = request.headers.get('Authorization')
        headers = {
            "Authorization": jwt,  # Add JWT Token here
            "Content-Type": "application/json"
        }

        data = {
            "id_reksadana": reksadana_id,
            "nominal": encode_value(nominal),
        }

        requests.post(
            f"{base_url}/dashboard/process-payment/",  # Full URL
            json=data,
            headers=headers, 
        )
        
        return redirect('/dashboard/')

    #TODO: Bikin html buy page
    return render(request, "buy_page.html", context={'reksadana_id':reksadana_id})

# async function call
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        res = create_payment(request)
        if res.status_code != 201:
            res_data = json.loads(res.content.decode('utf-8'))
            return JsonResponse(res_data, status=400)
        

        res = create_unit_dibeli(request)
        if res.status_code != 201:
            res_data = json.loads(res.content.decode('utf-8'))
            return JsonResponse(res_data, status=400)
        
        return JsonResponse({"message": "Successfully processed payment"}, status=201)