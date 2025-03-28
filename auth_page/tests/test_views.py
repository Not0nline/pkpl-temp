from unittest.mock import patch, MagicMock
from django.test import RequestFactory, TestCase
from django.http import HttpRequest
from django.conf import settings
from django.urls import reverse
import jwt
import datetime
from auth_page.views import home_view, login_view, logout_view, register_view
from tibib.middleware import JWTAuthenticationMiddleware

class TestJWTAuthenticationMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = lambda request: HttpRequest()
        self.middleware = JWTAuthenticationMiddleware(self.get_response)
        self.valid_payload = {
            'id': 1,
            'full_phone': '1234567890',
            'role': 'user',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        self.secret_key = settings.JWT_SECRET_KEY

    def test_exempt_paths(self):
        exempt_paths = ['/login/', '/register/', '/static/', '/admin/', '/favicon.ico']
        for path in exempt_paths:
            request = self.factory.get(path)
            response = self.middleware(request)
            self.assertIsInstance(response, HttpRequest, f"Path {path} should be exempted")

    def test_valid_auth_header(self):
        token = jwt.encode(self.valid_payload, self.secret_key, algorithm="HS256")
        request = self.factory.get('/home/', HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.middleware(request)
        self.assertEqual(request.user_id, self.valid_payload['id'])
        self.assertEqual(request.user_username, self.valid_payload['full_phone'])
        self.assertEqual(request.user_role, self.valid_payload['role'])

    def test_valid_auth_cookie(self):
        token = jwt.encode(self.valid_payload, self.secret_key, algorithm="HS256")
        request = self.factory.get('/home/')
        request.COOKIES['jwt_token'] = f'Bearer {token}'
        response = self.middleware(request)
        self.assertEqual(request.user_id, self.valid_payload['id'])
        self.assertEqual(request.user_username, self.valid_payload['full_phone'])
        self.assertEqual(request.user_role, self.valid_payload['role'])

    def test_expired_token_auth_header(self):
        expired_payload = self.valid_payload.copy()
        expired_payload['exp'] = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        token = jwt.encode(expired_payload, self.secret_key, algorithm="HS256")
        request = self.factory.get('/home/', HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.middleware(request)
        self.assertIn(response.status_code, [401, 302])

    def test_expired_token_auth_cookie(self):
        expired_payload = self.valid_payload.copy()
        expired_payload['exp'] = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        token = jwt.encode(expired_payload, self.secret_key, algorithm="HS256")
        request = self.factory.get('/home/')
        request.COOKIES['jwt_token'] = f'Bearer {token}'
        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_auth_header(self):
        invalid_token = 'invalid.token.here'
        request = self.factory.get('/home/', HTTP_AUTHORIZATION=f'Bearer {invalid_token}')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 401)

    def test_missing_token(self):
        request = self.factory.get('/home/')
        response = self.middleware(request)
        self.assertIn(response.status_code, [401, 302])

class TestRegisterView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('requests.post')
    def test_successful_registration(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        data = {
            'phone_number': '1234567890',
            'country_code': '+1',
            'card_number': '1234 5678 9012 3456',
            'password': 'securepassword'
        }
        request = self.factory.post(reverse('auth_page:register'), data)
        response = register_view(request)

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(response.url, reverse('auth_page:login'))

    @patch('requests.post')
    def test_failed_registration(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        data = {
            'phone_number': '1234567890',
            'country_code': '+1',
            'card_number': '1234 5678 9012 3456',
            'password': 'securepassword'
        }
        request = self.factory.post(reverse('auth_page:register'), data)
        response = register_view(request)

        self.assertEqual(response.status_code, 200)  # Render register.html with error
        self.assertContains(response, 'Registration failed. Please try again.')

    @patch('requests.post')
    def test_exception_during_registration(self, mock_post):
        mock_post.side_effect = Exception("API Error")

        data = {
            'phone_number': '1234567890',
            'country_code': '+1',
            'card_number': '1234 5678 9012 3456',
            'password': 'securepassword'
        }
        request = self.factory.post(reverse('auth_page:register'), data)
        response = register_view(request)

        self.assertEqual(response.status_code, 200)  # Render register.html with error

class TestLoginView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('requests.post')
    def test_successful_login(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Authorization": "valid.jwt.token"}
        mock_post.return_value = mock_response

        data = {
            'country_code': '+1',
            'phone_number': '1234567890',
            'password': 'securepassword'
        }
        request = self.factory.post(reverse('auth_page:login'), data)
        response = login_view(request)

        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertEqual(response.url, reverse('auth_page:home'))
        self.assertIn('jwt_token', response.cookies)
        self.assertEqual(response.cookies['jwt_token'].value, 'valid.jwt.token')

    @patch('requests.post')
    def test_failed_login(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        data = {
            'country_code': '+1',
            'phone_number': '1234567890',
            'password': 'wrongpassword'
        }
        request = self.factory.post(reverse('auth_page:login'), data)
        response = login_view(request)

        self.assertEqual(response.status_code, 200)  # Render login.html with error
        self.assertContains(response, 'Login failed. Please check your credentials.')

    @patch('requests.post')
    def test_exception_during_login(self, mock_post):
        mock_post.side_effect = Exception("API Error")

        data = {
            'country_code': '+1',
            'phone_number': '1234567890',
            'password': 'securepassword'
        }
        request = self.factory.post(reverse('auth_page:login'), data)
        response = login_view(request)

        self.assertEqual(response.status_code, 200)  # Render login.html with error
        self.assertContains(response, 'An error occurred: API Error')

class TestHomeView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def apply_middleware(self, request):
        middleware = JWTAuthenticationMiddleware(lambda x: x)
        middleware(request)

    def test_home_view_with_authenticated_user(self):
        request = self.factory.get(reverse('auth_page:home'))
        token = jwt.encode({
            'id': 1,
            'full_phone': '1234567890',
            'role': 'user',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, settings.JWT_SECRET_KEY, algorithm="HS256")
        request.COOKIES['jwt_token'] = f'Bearer {token}'
        self.apply_middleware(request)

        response = home_view(request)
        self.assertEqual(response.status_code, 200)