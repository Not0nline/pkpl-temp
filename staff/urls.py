from django.urls import path
from staff.views import create_uwu, edit_uwu, show_dashboard

urlpatterns = [
    path('dashboard/', show_dashboard, name="dashboard_admin"),
    path('create_reksadana/', create_uwu, name="create_reksadana"),
    path('edit_reksadana/', edit_uwu, name="edit_reksadana"),
]
