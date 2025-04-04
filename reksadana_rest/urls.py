from django.urls import path
from .views import *

app_name = 'reksadana_rest'

urlpatterns = [
    path('create-reksadana/',create_reksadana, name="create_reksadana"),
    path('get-all-reksadana/',get_all_reksadana, name="get_all_reksadana"),
    path("create-unitdibeli/", create_unit_dibeli, name="create_unit_dibeli"),
    path("get-unitdibeli-by-user/", get_units_by_user, name="get_units_by_user"),
    path('get-reksadana-history/<uuid:id_reksadana>/', get_reksadana_history, name="get_reksadana_history"),
    path('edit-reksadana/', edit_reksadana, name="edit_reksadana"),
    path('payment-gateway/', check_payment_gateway_status, name="payment_gateway"),
]
