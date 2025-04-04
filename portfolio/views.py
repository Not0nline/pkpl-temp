import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

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
        data = json.loads(get_units_by_user(request).content)

        #TODO: Blm bikin portfolio.html
        # di tiap unit dalam daftarnya ada tombol jual aja, biar
        # gk usah bikin file tampilin detail lagi 
        # Jangan lupa buat simpen id unitdibeli supaya bisa sell
        return render(request, 'portfolio.html', context={"units": data})
    return JsonResponse({"error": "Invalid request method"}, status=405)

# TODO: Not tested with postman
@csrf_exempt
def jual_unitdibeli(request):
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method=='POST':
        #Process jual
        data = json.loads(request.body)
        id_unitdibeli = data.get("id_unitdibeli")

        base_url = settings.BASE_BACKEND_URL  # Example: "http://127.0.0.1:8000"
        jwt = request.headers.get("Authorization")
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