from django.urls import path

from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("beli-unit/", beli_unit, name="beli_unit"),
    path('process-payment/', process_payment, name="process_payment")
]