import json

import requests
import httpx
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from reksadana_rest.views import get_all_reksadana, create_unit_dibeli, create_payment

# Create your views here.
def index(request):
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    reksadanas = json.loads(get_all_reksadana(request).content)['reksadana']
    #TODO: Bikin html dashboard
    return render(request, "dashboard.html", context=reksadanas)

#TODO: NOT TESTED BY POSTMAN

def beli_unit(request, reksadana_id):
    if not hasattr(request, "user_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method=='POST':
        #Simulate third party payment
        #TODO: Encode data
        data = json.loads(request.body)
        id_unitdibeli = data.get("id_unitdibeli")
        
        base_url = settings.BASE_BACKEND_URL  # Example: "http://127.0.0.1:8000"
        jwt = request.headers.get('Authorization')
        headers = {
            "Authorization": f"Bearer {jwt}",  # Add JWT Token here
            "Content-Type": "application/json"
        }

        requests.post(
            f"{base_url}/dashboard/process-payment/",  # Full URL
            son={"id_unitdibeli": id_unitdibeli},
            headers=headers,  # Pass headers here
        )
        
        return redirect('/dashboard/')

    #TODO: Bikin html buy page
    return render(request, "buy_page.html", context={'reksadana_id':reksadana_id})

# async function call
def process_payment(request):
    if request.method == 'POST':
        #TODO: Decode data
        create_payment(request)
        create_unit_dibeli(request)