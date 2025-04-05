import json
import requests
from django.conf import settings

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from reksadana_rest.views import get_units_by_user, delete_unit_dibeli_by_id, get_unit_dibeli_by_id
from tibib.utils import sanitize_input, handle_error, decrypt_and_verify

def index(request):
    """
    Handle portfolio index page rendering
    """
    if request.user_role != 'user':
        return handle_error(request, 403, "Forbidden: You don't have permission to access this page")
    
    if request.method != 'GET':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Ensure user_id is set on request if it's in the session
        if hasattr(request, 'session') and not hasattr(request, 'user_id') and 'user_id' in request.session:
            request.user_id = request.session['user_id']
        
        # Ensure Authorization header is set if token is in session
        if hasattr(request, 'session') and 'token' in request.session and not request.META.get('HTTP_AUTHORIZATION'):
            request.META['HTTP_AUTHORIZATION'] = request.session['token']
        
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
            'user_role':request.user_role
        })
    
    except json.JSONDecodeError:
        return render(request, 'portfolio.html', context={
            "error": "Invalid response format",
            "units": [],
        })
    except Exception as e:
        return render(request, 'portfolio.html', context={
            "error": f"Error loading portfolio: {str(e)}",
            "units": [],
        })

def jual_unitdibeli(request):
    """
    Process selling a unit
    """
    if request.user_role != 'user':
        return handle_error(request, 403, "Forbidden: You don't have permission to access this page")
    
    # Ensure user is authenticated
    if not request.user_id:
        messages.error(request, "Unauthorized access")
        return redirect('auth_page:login')

    if request.method != 'POST':
        messages.error(request, "Invalid request method")
        return redirect('portfolio:index')

    # Get the unit ID to sell
    id_unitdibeli = sanitize_input(request.POST.get("id_unitdibeli"))
    
    if not id_unitdibeli:
        messages.error(request, "Missing unit ID")
        return redirect('portfolio:index')

    try:
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

        res = get_unit_dibeli_by_id(request, id_unitdibeli)
        if response.status_code != 200:
            error_data = json.loads(response.content.decode('utf-8'))
            return render(request, "error.html", {
                "error": f"Selling units failed: {error_data.get('error', 'Unknown error')}",
                "back_url": "/"
            })

        data = json.loads(res.content.decode('utf-8'))  # Convert response to dictionary
        nav_dibeli = data.get('nav_dulu',1)
        nav_sekarang = data.get('nav_sekarang',1)
        total_beli = data.get('total_beli',1)
        card_data['amount'] = nav_dibeli/nav_sekarang*total_beli  
        
        # Make API request
        response = requests.post(f"{settings.API_URL}/reksadana/payment-gateway/", 
                                json=card_data, 
                                headers={'Content-Type': 'application/json', 'Authorization': request.COOKIES.get('jwt_token')})

        if response.status_code != 200:
            error_data = json.loads(response.content.decode('utf-8'))
            return render(request, "error.html", {
                "error": f"Payment failed: {error_data.get('error', 'Unknown error')}",
                "back_url": "/"
            })
        
        else:
            data = response.json()  # Convert response to dictionary

            # Prepare request body
            request._body = json.dumps({
                "id_unitdibeli": id_unitdibeli
            }).encode('utf-8')

            response = delete_unit_dibeli_by_id(request)
            data = json.loads(response.content)
            nav_dibeli = data.get('nav_dulu',1)
            nav_sekarang = data.get('nav_sekarang',1)
            total_beli = data.get('total_beli',1)
            # Check response status
            if response.status_code == 200:
                print("Successfully sold unit reksadana seharga",nav_sekarang/nav_dibeli*total_beli)
                messages.success(request, f"Successfully sold unit reksadana seharga {nav_sekarang/nav_dibeli*total_beli}")
            else:
                # Attempt to parse error message
                try:
                    error_data = json.loads(response.content.decode('utf-8')) 
                    messages.error(request, error_data.get('error', 'Failed to sell unit')) 
                except (json.JSONDecodeError, UnicodeDecodeError): 
                    messages.error(request, 'Failed to sell unit') 

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('portfolio:index')

def process_sell(request):
    """
    Validate and process the sell request
    """
    if request.user_role != 'user':
        return handle_error(request, 403, "Forbidden: You don't have permission to access this page")
    
    # Ensure user is authenticated
    if not request.user_id:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Parse request body
        try:
            request_body = json.loads(request.body.decode('utf-8'))
            id_unitdibeli = sanitize_input(request_body.get('id_unitdibeli'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid request body"}, status=400)

        if not id_unitdibeli:
            return JsonResponse({"error": "Missing unit ID"}, status=400)

        # Call delete function
        response = delete_unit_dibeli_by_id(request)

        # Check response status
        if response.status_code == 201:
            return JsonResponse({"message": "Successfully sold unit reksadana"}, status=201)
        else:
            # Attempt to parse error message
            try:
                error_data = json.loads(response.content.decode('utf-8')) 
                return JsonResponse({"error": error_data.get('error', 'Failed to sell unit')}, status=400) 
            except (json.JSONDecodeError, UnicodeDecodeError): 
                return JsonResponse({"error": "Failed to sell unit"}, status=400) 

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)