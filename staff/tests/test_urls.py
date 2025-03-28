from django.test import SimpleTestCase
from django.urls import resolve, reverse
from staff.views import show_dashboard, create_reksadana_staff, edit_reksadana_staff
class TestUrls(SimpleTestCase):
    def test_url_show_dashboard(self):
        url = reverse("staff:dashboard_admin")
        self.assertEqual(url, '/staff/dashboard/')
        self.assertEqual(resolve(url).func, show_dashboard)
    def test_url_create_reksadana(self):
        url = reverse("staff:create_reksadana")
        self.assertEqual(url, '/staff/create_reksadana/')
        self.assertEqual(resolve(url).func, create_reksadana_staff)
    def test_url_edit_reksadana(self):
        url = reverse("staff:edit_reksadana")
        self.assertEqual(url, '/staff/edit_reksadana/')
        self.assertEqual(resolve(url).func, edit_reksadana_staff)