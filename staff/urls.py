from django.urls import path
from staff.views import create_reksadana, edit_reksadana, show_dashboard

urlpatterns = [
    path('dashboard/', show_dashboard, name="dashboard_admin"),
    path('create_reksadana/', create_reksadana, name="create_reksadana"),
    path('edit_reksadana/', edit_reksadana, name="edit_reksadana"),
]
