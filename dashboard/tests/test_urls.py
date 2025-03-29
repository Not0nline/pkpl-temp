from django.test import SimpleTestCase
from django.urls import resolve, reverse
from dashboard.views import beli_unit, dashboard, process_payment

class TestUrls(SimpleTestCase):
    def test_url_dashboard(self):
        url = reverse("dashboard:dashboard")
        self.assertEqual(url, '/dashboard/')
        self.assertEqual(resolve(url).func, dashboard)
    def test_url_beli_unit(self):
        url = reverse("dashboard:beli_unit")
        self.assertEqual(url, '/dashboard/beli-unit/')
        self.assertEqual(resolve(url).func, beli_unit)
    def test_url_home(self):
        url = reverse("dashboard:process_payment")
        self.assertEqual(url, '/dashboard/process-payment/')
        self.assertEqual(resolve(url).func, process_payment)