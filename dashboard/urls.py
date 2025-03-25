from django.urls import path

from .views import *

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("beli-unit/", beli_unit, name="beli_unit"),
    path('process-payment/', process_payment, name="process_payment")
]