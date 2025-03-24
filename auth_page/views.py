from django.shortcuts import render, redirect
from django.http import JsonResponse
import os
import requests
import jwt
from django.conf import settings

API_BASE_URL = os.environ.get('API_BASE_URL')

def register_view(request):
    if request.method == 'POST':
        try:
            # Get data from form
            nama = request.POST.get('nama')
            phone_number = request.POST.get('phone_number')
            country_code = request.POST.get('country_code')
            card_number = request.POST.get('card_number').replace(' ', '')  
            password = request.POST.get('password')
            
            # Prepare data for API
            payload = {
                "nama": nama,
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
            country_code = request.POST.get('country_code')
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
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
                request.session['token'] = data.get('Authorization')
                request.session['user_role'] = data.get('role')
                request.session['phone_number'] = phone_number
                request.session['country_code'] = country_code
                try:
                    token = data.get('Authorization').split(' ')[1]
                    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
                    request.session['user_id'] = payload.get('id')
                    request.session['card_number'] = payload.get('card_number')
                    request.session['nama']= payload.get('nama')
                except Exception as e:
                    print(f"Error decoding JWT: {e}")
                
                request.session.modified = True
                
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
        'nama': request.session.get('nama', 'Unknown'),
        'user_role': request.session.get('user_role', 'Unknown'),
        'phone_number': request.session.get('phone_number', 'Unknown'),
        'country_code': request.session.get('country_code', 'Unknown'),
        'card_number': request.session.get('card_number', 'Unknown')
        })

def logout_view(request):
    request.session.flush()
    
    # Redirect to login page
    return redirect('login')