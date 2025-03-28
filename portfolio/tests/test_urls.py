from django.test import SimpleTestCase
from django.urls import resolve, reverse
from portfolio.views import jual_unitdibeli, process_sell
class TestUrls(SimpleTestCase):
    def test_url_jual_unitdibeli(self):
        url = reverse("portfolio:jual_unitdibeli")
        self.assertEqual(url, '/portfolio/jual-unitdibeli/')
        self.assertEqual(resolve(url).func, jual_unitdibeli)
    def test_url_process_sell(self):
        url = reverse("portfolio:proccess_sell")
        self.assertEqual(url, '/portfolio/process-sell/')
        self.assertEqual(resolve(url).func, process_sell)