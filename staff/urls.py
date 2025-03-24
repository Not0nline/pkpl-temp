from django.urls import path
from .views import create_reksadana, edit_reksadana, daftar_reksadana

urlpatterns = [
    path('daftar_reksadana/', daftar_reksadana, name="daftar_reksadana"),
    path('create_reksadana/', create_reksadana, name="create_reksadana"),
    path('edit_reksadana/', edit_reksadana, name="edit_reksadana"),
]
