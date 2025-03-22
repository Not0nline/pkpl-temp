from django.urls import path
from .views import *

urlpatterns = [
    path('',index, name="index"),
    path('process-sell', process_sell, name="proccess_sell")
]
