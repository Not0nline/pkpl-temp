from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import requests
from tibib.utils import sanitize_input

API_BASE_URL = os.environ.get('API_BASE_URL')

def register_view(request):
    if request.method == 'POST':
        try:
            # Get data from form
            phone_number = request.POST.get('phone_number')
            country_code = request.POST.get('country_code')
            card_number = request.POST.get('card_number').replace(' ', '')  
            password = request.POST.get('password')
            
            # Prepare data for API
            payload = {
                "phone_number": sanitize_input(phone_number),
                "country_code": sanitize_input(country_code),
                "card_number": sanitize_input(card_number),
                "password": sanitize_input(password)
            }
            
            # Make API request
            response = requests.post(f"{API_BASE_URL}/register/",
                                     json=payload,
                                     headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                return redirect('auth_page:login')
            else:
                return render(request, 'register.html', {
                    'error': response.json().get('error', 'Registration failed. Please try again.')
                })
        except Exception as e:
            return render(request, 'register.html', {
                'error': f'An error occurred: {str(e)}'
            })
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        try:
            country_code = request.POST.get('country_code')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            full_phone = f"{country_code}{phone_number}"
            
            # Prepare data for API
            payload = {
                "full_phone": sanitize_input(full_phone),
                "password": password
            }
            
            # Make API request
            response = requests.post(f"{API_BASE_URL}/login/", 
                                    json=payload, 
                                    headers={'Content-Type': 'application/json'})
            
            data = response.json()  # Convert response to dictionary
            token = data.get("Authorization")  # Get the token
            if response.status_code == 200:
                response = redirect('auth_page:home')
                response.set_cookie(
                    key="jwt_token",
                    value=token,
                    httponly=True,  # Prevents JavaScript access (more secure)
                    samesite="Lax",  # Prevents CSRF (change to "Strict" if necessary)
                    secure=False  
                )
                return response
            else:
                return render(request, 'login.html', {
                    'error': 'Login failed. Please check your credentials.'
                })
        except Exception as e:
            return render(request, 'login.html', {
                'error': f'An error occurred: {str(e)}'
            })
    
    return render(request, 'login.html')

def home_view(request):
    # Get user attributes if they exist, otherwise use None as fallback
    user_role = getattr(request, 'user_role', None)
    phone_number = getattr(request, 'user_username', None)
    
    return render(request, 'home.html', {
        'user_role': user_role,
        'phone_number': phone_number,
    })

def logout_view(request):
    response = redirect('auth_page:login')
    response.delete_cookie("jwt_token")
    return response

def handler404(request,*args, **argv):
    return render(request, "404.html", context={"user_role":request.user_role})
