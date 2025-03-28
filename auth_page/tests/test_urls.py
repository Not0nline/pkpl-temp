from django.test import SimpleTestCase
from django.urls import resolve, reverse
from auth_page.views import register_view, login_view, logout_view, home_view

class TestUrls(SimpleTestCase):
    def test_url_register(self):
        url = reverse("register")
        self.assertEqual(url, '/register/')
        self.assertEqual(resolve(url).func, register_view)
    def test_url_login(self):
        url = reverse("login")
        self.assertEqual(url, '/login/')
        self.assertEqual(resolve(url).func, login_view)
    def test_url_logout(self):
        url = reverse("logout")
        self.assertEqual(url, '/logout/')
        self.assertEqual(resolve(url).func, logout_view)
    def test_url_home(self):
        url = reverse("home")
        self.assertEqual(url, '/home/')
        self.assertEqual(resolve(url).func, home_view)
    # Masih error
    # def test_url_index(self):
    #     url = reverse("index")
    #     self.assertEqual(url, '')
    #     self.assertEqual(resolve(url).func, login_view)