<<<<<<< HEAD
from django.shortcuts import render

# Create your views here.
=======
from django.shortcuts import redirect, render
from reksadana_rest.views import *


def daftar_reksadana(request):
    return render(request, "daftar_reksadana.html",context=get_all_reksadana(request).content)
    
# Create your views here.
def create_uwu(request):
    if request.method == 'POST':
        create_reksadana(request)
        return redirect('/staff/daftar_reksadana/')
    return render(request, "create_reksadana.html", context={})

def edit_uwu(request):
    if request.method == 'POST':
        edit_reksadana(request)
        return redirect('/staff/daftar_reksadana/')
    return render(request, "edit_reksadana.html", context={})
>>>>>>> 2c8d3c8ba2b73a73ce6e55c3ea0f291ad7c2204f
