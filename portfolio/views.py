import json

import requests
import httpx
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from reksadana_rest.views import get_units_by_user,delete_unit_dibeli_by_id

# TODO: Not tested with postman
def index(request):
    if request.method == 'GET':
        data = json.loads(get_units_by_user(request).content)

        #TODO: Blm bikin portfolio.html
        # di tiap unit dalam daftarnya ada tombol jual aja, biar
        # gk usah bikin file tampilin detail lagi 
        # Jangan lupa buat simpen id unitdibeli supaya bisa sell
        return render(request, 'portfolio.html', context=data)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# TODO: Not tested with postman
def jual_unitdibeli(request):
    if request.method=='POST':
        #TODO: Encode body
        #Process jual
        data = json.loads(request.body)
        id_unitdibeli = data.get("id_unitdibeli")

        base_url = settings.BASE_BACKEND_URL  # Example: "http://127.0.0.1:8000"
        jwt = request.headers.get("Authorization")
        headers = {
            "Authorization": f"Bearer {jwt}",  # Add JWT Token here
            "Content-Type": "application/json"
        }

        requests.post(
            f"{base_url}/portfolio/process-sell/",  # Full URL
            son={"id_unitdibeli": id_unitdibeli},
            headers=headers,  # Pass headers here
        )

        return redirect('/portfolio/')

# TODO: Not tested with postman
def process_sell(request):
    if request.method=='POST':
        #TODO: Decode body
        #Process jual
        delete_unit_dibeli_by_id(request)
        return redirect('/portfolio/')