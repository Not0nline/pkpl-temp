from django.urls import path, include
from .views import *

urlpatterns = [
    path('',index, name="index"),
    path('jual-unitdibeli/', jual_unitdibeli, name="jual_unitdibeli"),

    # ini simulasi third party
    path('process-sell/', process_sell, name="proccess_sell"),
]
