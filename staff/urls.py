from django.urls import path
from .views import create_uwu, edit_uwu

urlpatterns = [
    path('create-uwu', create_uwu,name="create-reksadana"),
    path('edit-uwu', edit_uwu,name="edit-reksadana"),
]
