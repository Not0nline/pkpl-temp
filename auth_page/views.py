# auth_page/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from .forms import (
    # CustomUserCreationForm, 
    # CustomAuthenticationForm
# )

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('login')

def register_view(request):
    pass
    # if request.method == 'POST':
    #     form = CustomUserCreationForm(request.POST)
    #     if form.is_valid():
    #         user = form.save()
    #         login(request, user)
    #         messages.success(request, "Registration successful!")
    #         return redirect('home')
    #     else:
    #         # If there are form errors, they will be displayed in the template
    #         pass
    # else:
    #     form = CustomUserCreationForm()
    
    # return render(request, 'auth_page/register.html', {'form': form})

def login_view(request):
    pass
    # if request.method == 'POST':
    #     form = CustomAuthenticationForm(request, data=request.POST)
    #     if form.is_valid():
    #         phone_number = form.cleaned_data.get('username')
    #         password = form.cleaned_data.get('password')
    #         user = authenticate(request, username=phone_number, password=password)
    #         if user is not None:
    #             login(request, user)
    #             messages.success(request, "Login successful!")
    #             return redirect('home')
    #         else:
    #             messages.error(request, "Invalid phone number or password.")
    #     else:
    #         # If there are form errors, they will be displayed in the template
    #         pass
    # else:
    #     form = CustomAuthenticationForm()
    
    # return render(request, 'auth_page/login.html', {'form': form})

@login_required
def home_view(request):
    # Format the card number to show only last 4 digits
    card_number = request.user.card_number
    masked_card = f"**** **** **** {card_number[-4:]}"
    
    context = {
        'user': request.user,
        'masked_card': masked_card
    }
    return render(request, 'auth_page/home.html', context)