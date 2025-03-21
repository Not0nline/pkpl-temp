from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import requests

# API endpoint
API_BASE_URL = "http://localhost:8001"

def register_view(request):
    if request.method == 'POST':
        try:
            # Get data from form
            phone_number = request.POST.get('phone_number')
            country_code = request.POST.get('country_code')
            card_number = request.POST.get('card_number').replace(' ', '')  # Remove spaces from card number
            password = request.POST.get('password')
            
            # Prepare data for API
            payload = {
                "phone_number": phone_number,
                "country_code": country_code,
                "card_number": card_number,
                "password": password
            }
            
            # Make API request
            response = requests.post(f"{API_BASE_URL}/register/", 
                                     json=payload, 
                                     headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                return redirect('login')
            else:
                return render(request, 'register.html', {
                    'error': 'Registration failed. Please try again.'
                })
        except Exception as e:
            return render(request, 'register.html', {
                'error': f'An error occurred: {str(e)}'
            })
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        try:
            # Get data from form
            country_code = request.POST.get('country_code')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            
            # Create full phone number
            full_phone = f"{country_code}{phone_number}"
            
            # Prepare data for API
            payload = {
                "full_phone": full_phone,
                "password": password
            }
            
            # Make API request
            response = requests.post(f"{API_BASE_URL}/login/", 
                                    json=payload, 
                                    headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                # Store JWT token in session
                request.session['token'] = data.get('Authorization')
                request.session['user_role'] = data.get('role')
                return redirect('home')
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
    if 'token' not in request.session:
        return redirect('login')
    
    return render(request, 'home.html', {
        'user_role': request.session.get('user_role', 'Unknown'),
        'phone_number': request.session.get('phone_number', 'Unknown'),
        'country_code': request.session.get('country_code', 'Unknown'),
        'card_number': request.session.get('card_number', 'Unknown')
    })

def logout_view(request):
    # Clear session data
    if 'token' in request.session:
        del request.session['token']
    if 'user_role' in request.session:
        del request.session['user_role']
    
    # Redirect to login page
    return redirect('login')