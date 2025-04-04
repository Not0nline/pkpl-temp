import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from reksadana_rest.views import get_all_reksadana, create_unit_dibeli, get_reksadana_history
import requests
from tibib.utils import encrypt_and_sign, sanitize_input, decrypt_and_verify


def dashboard(request):
    # Check authentication using both request attributes and session
    user_id = getattr(request, 'user_id', None) 
    if not user_id:
        return redirect('auth_page:login')
        
    try:
        # Get all reksadana data
        response = get_all_reksadana(request)
        if response.status_code != 200:
            return render(request, "dashboard.html", {
                "error": "Failed to load reksadana data",
                "user_name": request.user_username
            })
        
        # Parse response
        data = json.loads(response.content)
        reksadanas = data.get('reksadanas', [])
        
        # Fetch history for each reksadana
        for reksadana in reksadanas:
            history_response = get_reksadana_history(request, reksadana['id_reksadana'])
            if history_response.status_code == 200:
                reksadana['history'] = json.loads(history_response.content)
            else:
                reksadana['history'] = []

        # Ini perlu di duplikat kodenya, gegara nav dan aum berubah pas get_reksadana_history
        #####################################
        reksadanas2 = get_all_reksadana(request)
        # Parse response
        data = json.loads(reksadanas2.content)
        reksadanas2 = data.get('reksadanas', [])
        print(reksadanas2)

        for reksadana in reksadanas2:
            history_response = get_reksadana_history(request, reksadana['id_reksadana'])
            if history_response.status_code == 200:
                reksadana['history'] = json.loads(history_response.content)
            else:
                reksadana['history'] = []
        
        #####################################


        return render(request, "dashboard.html", {
            "reksadanas": reksadanas2,
            "user_name": request.user_username
        })
        
    except Exception as e:
        return render(request, "dashboard.html", {
            "error": f"An error occurred: {str(e)}",
            "user_name": request.user_username
        })

# @csrf_exempt
def beli_unit(request):
    user_id = getattr(request, 'user_id', None) 
    if not user_id:
        return redirect('auth_page:login')
        
    if request.method == 'POST':
        try:
            # Handle form submission
            if request.content_type == 'application/json':
                # Handle JSON data (API calls)
                data = json.loads(request.body)
                reksadana_id = sanitize_input(data.get("id_reksadana"))
                nominal = sanitize_input(data.get("nominal"), True)
            else:
                # Handle form data (HTML form)
                reksadana_id = sanitize_input(request.POST.get("id_reksadana"))
                nominal = sanitize_input(request.POST.get("nominal"), True)

            # Validate required fields
            if not reksadana_id or not nominal:
                return render(request, "error.html", {
                    "error": "Missing required fields",
                    "back_url": "/"
                })
                
            # try:
            nominal = float(nominal)
            if nominal < 10000:  # Minimum investment amount
                return render(request, "error.html", {
                    "error": "Minimum investment amount is Rp 10,000",
                    "back_url": "/"
                })
            # except ValueError:
            #     return render(request, "error.html", {
            #         "error": "Invalid amount format",
            #         "back_url": "/"
            #     })

            # get user's credit card
            response = requests.post(f"{settings.API_BASE_URL}/get-card/", 
                                    headers={'Authorization': request.COOKIES.get('jwt_token')})
            
            if response.status_code != 200:
                print("error ngambil card data")
                return render(request, "error.html", {
                    "error": "Failed to retrieve card information",
                    "back_url": "/"
                })
            
            card_data = response.json()
            print("card data: ", card_data)
            card_number = decrypt_and_verify(card_data['credit_card'], card_data['signature'])
            
            # Process payment
            return render(request, "payment_confirmation.html", {
                "reksadana_id": reksadana_id,
                "nominal": nominal,
                "user_id": user_id,
                "card_number": str(card_number)[2:len(str(card_number))-1],  # Remove b' and '
            })
        except Exception as e:
            return render(request, "error.html", {
                "error": f"An error occurred: {str(e)}",
                "back_url": "/"
            })
    
    # GET request - redirect to dashboard
    return redirect('dashboard:dashboard')

# async function call
# @csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        try:
            user_id = getattr(request, 'user_id', None) 
            if not user_id:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = {
                    'user_id': sanitize_input(request.session.get('user_id')),
                    'id_reksadana': sanitize_input(request.POST.get('id_reksadana')),
                    'nominal': sanitize_input(request.POST.get('nominal'), True),
                }

            if not data.get('id_reksadana') or not data.get('nominal'):
                return JsonResponse({"error": "Missing required fields"}, status=400)
            
            nominal_int = data.get('nominal')
        
            # Also prepare the JSON body for the API functions
            nominal_encrypted, signature = encrypt_and_sign(str(nominal_int))
            request._body = json.dumps({
                'id_reksadana': data.get('id_reksadana'),
                'signature': signature,
                'nominal': nominal_encrypted,
            }).encode('utf-8')
            
            # get user's credit card
            response = requests.post(f"{settings.API_BASE_URL}/get-card/", 
                                    headers={'Authorization': request.COOKIES.get('jwt_token')})
            
            if response.status_code != 200:
                return render(request, "error.html", {
                    "error": "Failed to retrieve card information",
                    "back_url": "/"
                })
            
            card_data = response.json()
            decrypt_and_verify(card_data['credit_card'], card_data['signature'])
            card_data['nominal'] = nominal_int
            
            # Make API request
            response = requests.post(f"{settings.API_URL}/reksadana/payment-gateway/", 
                                    json=card_data, 
                                    headers={'Content-Type': 'application/json', 'Authorization': request.COOKIES.get('jwt_token')})
            
            count = 0
            while response.status_code == 402 and count < 4:
                response = requests.post(f"{settings.API_URL}/reksadana/payment-gateway/", 
                                    json=card_data, 
                                    headers={'Content-Type': 'application/json', 'Authorization': request.COOKIES.get('jwt_token')})
                count += 1

            if response.status_code != 200:
                error_data = json.loads(response.content.decode('utf-8'))
                return render(request, "error.html", {
                    "error": f"Payment failed: {error_data.get('error', 'Unknown error')}",
                    "back_url": "/"
                })
            
            else:
                data = response.json()  # Convert response to dictionary

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
                return redirect('portfolio:index')
            
        except Exception as e:
            print(f"Exception in process_payment: {str(e)}")
            return render(request, "error.html", {
                "error": f"An error occurred: {str(e)}",
                "back_url": "/"
            })

    return HttpResponse("Method not allowed", status=405)
