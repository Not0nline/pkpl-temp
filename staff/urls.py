from django.urls import path
from staff.views import create_reksadana_staff, edit_reksadana_staff, show_dashboard

app_name = 'staff'

urlpatterns = [
    path('dashboard/', show_dashboard, name="dashboard_admin"),
    path('create_reksadana/', create_reksadana_staff, name="create_reksadana"),
    path('edit_reksadana/', edit_reksadana_staff, name="edit_reksadana"),
]
