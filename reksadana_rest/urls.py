from django.urls import path
from .views import *

urlpatterns = [
    path('create-reksadana',create_reksadana, name="create_reksadana"),
    path('get-all-reksadana',get_all_reksadana, name="get_all_reksadana"),
    path("create-payment/", create_payment, name="create_payment"),
    path("get-payment-by-user/<uuid:user_id>/", get_payments_by_user, name="get_payments_by_user"),
    path("create-unitdibeli", create_unit_dibeli, name="create_unit_dibeli"),
    path("get-unitdibeli-by-user/<uuid:user_id>/", get_units_by_user, name="get_units_by_user"),
]
