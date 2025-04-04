from django.shortcuts import render

def custom_404_view(request,*args, **argv):
    return render(request, "404.html", status=404)
