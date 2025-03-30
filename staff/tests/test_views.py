from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock

from staff.views import create_reksadana_staff, show_dashboard

class TestCreateReksadanaStaff(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:create_reksadana')  

    @patch('staff.views.requests.get')
    def test_missing_jwt_cookie(self, mock_requests_get):
        """
        If 'jwt_token' is missing in cookies, returns 401.
        """
        request = self.factory.post(self.url, data={})
        # No jwt_token in cookies
        response = create_reksadana_staff(request)

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {'error': 'Missing Authorization token'}
        )
        mock_requests_get.assert_not_called()

    @patch('staff.views.requests.get')
    @patch('staff.views.create_reksadana')
    def test_post_success_redirect(self, mock_create_reksadana, mock_requests_get):
        """
        If requests.get returns 200 (valid staff),
        and create_reksadana returns status_code=201,
        we expect a redirect to /staff/dashboard/.
        """
        mock_requests_get.return_value.status_code = 200

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_create_reksadana.return_value = mock_response

        request = self.factory.post(self.url, data={})
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = create_reksadana_staff(request)

        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.url, '/staff/dashboard/')
        mock_requests_get.assert_called_once()
        mock_create_reksadana.assert_called_once()

    @patch('staff.views.requests.get')
    @patch('staff.views.create_reksadana')
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    def test_post_create_reksadana_error(
        self, mock_get_categories, mock_get_banks,
        mock_create_reksadana, mock_requests_get
    ):
        """
        If requests.get returns 200 (valid staff),
        but create_reksadana returns non-201, 
        we expect to render 'create_reksadana.html' with an error message.
        """
        # Setup mocks
        mock_requests_get.return_value.status_code = 200

        mock_error_response = MagicMock()
        mock_error_response.status_code = 400
        mock_error_response.content = b'{"error": "Some creation error"}'
        mock_create_reksadana.return_value = mock_error_response

        mock_get_categories.return_value = [{'id': 1, 'name': 'CategoryA'}]
        mock_get_banks.return_value = [{'id': 10, 'name': 'BankX'}]

        request = self.factory.post(self.url, data={})
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = create_reksadana_staff(request)
        
        # A normal render(...) returns status 200 unless otherwise specified
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Some creation error', response.content)
        self.assertIn(b'BankX', response.content)      
        self.assertIn(b'CategoryA', response.content)  
        mock_requests_get.assert_called_once()
        mock_create_reksadana.assert_called_once()
        mock_get_categories.assert_called_once()
        mock_get_banks.assert_called_once()

    @patch('staff.views.requests.get')
    def test_post_invalid_staff(self, mock_requests_get):
        """
        If requests.get returns a non-200 (e.g., 403),
        we return a JSON error with the same status code.
        """
        mock_requests_get.return_value.status_code = 403

        request = self.factory.post(self.url, data={})
        request.COOKIES['jwt_token'] = 'test-jwt'

        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {'error': 'Unauthorized or forbidden access'}
        )

    @patch('staff.views.requests.get')
    def test_post_request_exception(self, mock_requests_get):
        """
        If requests.get raises an exception,
        the view returns a 503 JSON error.
        """
        mock_requests_get.side_effect = Exception("Connection error")
        
        request = self.factory.post(self.url, data={})
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 503)
        self.assertIn(b'error', response.content)

    # GET Request Tests
    @patch('staff.views.requests.get')
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    def test_get_success(self, mock_get_categories, mock_get_banks, mock_requests_get):
        """
        If requests.get returns 200 on a GET request,
        render the create_reksadana.html template with categories and banks.
        """
        mock_requests_get.return_value.status_code = 200
        mock_get_categories.return_value = [{'id': 1, 'name': 'CategoryA'}]
        mock_get_banks.return_value = [{'id': 10, 'name': 'BankX'}]

        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CategoryA', response.content)
        self.assertIn(b'BankX', response.content)
        mock_requests_get.assert_called_once()
        mock_get_categories.assert_called_once()
        mock_get_banks.assert_called_once()

    @patch('staff.views.requests.get')
    def test_get_invalid_staff(self, mock_requests_get):
        """
        If requests.get returns a non-200 (e.g., 401) on a GET request,
        we return a JSON error.
        """
        mock_requests_get.return_value.status_code = 401
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'

        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {'error': 'Unauthorized or forbidden access'}
        )

    @patch('staff.views.requests.get')
    def test_get_request_exception(self, mock_requests_get):
        """
        If requests.get raises an exception on a GET request,
        the view returns a 503 JSON error.
        """
        mock_requests_get.side_effect = Exception("Some GET error")
        
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 503)
        self.assertIn(b'error', response.content)

class TestShowDashboard(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:dashboard_admin')  
    
    @patch('staff.views.requests.get')
    def test_show_dashboard_missing_jwt(self, mock_requests_get):
        """
        If 'jwt_token' is missing in cookies, returns 401.
        """
        request = self.factory.get(self.url)
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {'error': 'Missing Authorization token'}
        )
        mock_requests_get.assert_not_called()
        
    @patch('staff.views.requests.get')
    def test_show_dashboard_get__request_exception(self, mock_requests_get):
        """
        If requests.get raises an exception on a GET request,
        the view returns a 503 JSON error.
        """
        mock_requests_get.side_effect = ConnectionError("Some GET error")
        
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 503)
        self.assertIn(b'error', response.content)
        self.assertIn(b'Auth service unavailable', response.content)

    # Valid Staff (requests.get -> 200)
    @patch('staff.views.fetch_all_reksadanas')
    @patch('staff.views.requests.get')
    def test_show_dashboard_valid_staff(self, mock_requests_get, mock_fetch_all):
        """
        If requests.get to /staff/ returns 200, the method should:
          - Call fetch_all_reksadanas()
          - Render 'dashboard_admin.html'
          - Pass the reksadanas in context
        """
        mock_requests_get.return_value.status_code = 200

        # Mock fetch_all_reksadanas return value
        mock_fetch_all.return_value = [
            {'id': 1, 'name': 'Some Reksadana'},
            {'id': 2, 'name': 'Another Reksadana'}
        ]

        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 200)
        # Check that 'reksadanas' is in the context
        self.assertIn(b'Some Reksadana', response.content)
        self.assertIn(b'Another Reksadana', response.content)
        mock_requests_get.assert_called_once()
        mock_fetch_all.assert_called_once()

    # Invalid Staff (requests.get -> e.g. 401)
    @patch('staff.views.requests.get')
    def test_show_dashboard_invalid_staff(self, mock_requests_get):
        """
        If requests.get returns a non-200 (403, 401, 500, etc.),
        the view should render 'error.html' with a forbidden message.
        """
        mock_requests_get.return_value.status_code = 401

        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'

        response = show_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unauthorized or forbidden access")

        mock_requests_get.assert_called_once()