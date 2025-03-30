from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
import requests
import json

from staff.views import show_dashboard, create_reksadana_staff, edit_reksadana_staff

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
    def test_show_dashboard_get_request_exception(self, mock_requests_get):
        """
        If requests.get raises an exception on a GET request,
        due to unavailable microservice
        """
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Some GET error")
        
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 503)
        self.assertIn(b'error', response.content)
        self.assertIn(b'Auth service unavailable', response.content)
        
    @patch('staff.views.requests.get')
    def test_show_dashboard_other_exception(self, mock_requests_get):
        """
        If requests.get raises other exception on a GET request
        """
        mock_requests_get.side_effect = Exception("Some error")
        
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'error', response.content)

    # Invalid Staff
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
        
    # Valid Staff
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
        self.assertIn(b'Some Reksadana', response.content)
        self.assertIn(b'Another Reksadana', response.content)
        mock_requests_get.assert_called_once()
        mock_fetch_all.assert_called_once()


class TestCreateReksadanaStaff(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:create_reksadana')  

    @patch('staff.views.requests.get')
    def test_create_missing_jwt_cookie(self, mock_requests_get):
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
    def test_create_post_request_success(self, mock_create_reksadana, mock_requests_get):
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
    def test_create_post_request_failed(
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
    def test_create_invalid_staff(self, mock_requests_get):
        """
        If the auth check (requests.get) returns non-200 status_code (e.g. 403),
        the view should return an unauthorized JSON response with that status.
        """

        request = self.factory.post(self.url, data={})
        request.COOKIES['jwt_token'] = 'test-jwt'
        
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_requests_get.return_value = mock_response

        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {'error': 'Unauthorized or forbidden access'}
        )

    # GET Request Tests
    @patch('staff.views.requests.get')
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    def test_create_get_request(self, mock_get_categories, mock_get_banks, mock_requests_get):
        """
        If request.method == 'GET' and staff is authenticated (status_code=200),
        render 'create_reksadana.html' with proper context.
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
    def test_create_invalid_staff(self, mock_requests_get):
        """
        If the auth check (requests.get) returns non-200 status_code (e.g. 403),
        the view should return an unauthorized JSON response with that status.
        """
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_requests_get.return_value = mock_response
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {"error": "Unauthorized or forbidden access"}
        )
        
    @patch('staff.views.requests.get')
    def test_create_auth_service_unavailable(self, mock_requests_get):
        """
        If the auth service is unavailable (ConnectionError),
        returns 503 with appropriate JSON message.
        """
        
        request = self.factory.get(self.url)
        # Simulate 'jwt_token' existing
        request.COOKIES['jwt_token'] = 'test-jwt'

        # Raise a ConnectionError to simulate auth service outage
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection lost")
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"error": "Auth service unavailable: Connection lost"}
        )
        
    @patch('staff.views.requests.get')
    def test_create_other_exceptions(self, mock_requests_get):
        """
        If some other unexpected exception is raised,
        returns 500 with the exception message.
        """
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'

        mock_requests_get.side_effect = Exception("Unexpected Error")
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {"error": "Unexpected Error"}
        )
        
class TestEditReksadanaStaff(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:edit_reksadana')  
        
    @patch('staff.views.requests.get')
    def test_edit_missing_jwt_cookie(self, mock_requests_get):
        """
        If 'jwt_token' is missing in cookies, returns 401.
        """
        request = self.factory.post(self.url, data={})
        # No jwt_token in cookies
        response = edit_reksadana_staff(request)

        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {'error': 'Missing Authorization token'}
        )
        mock_requests_get.assert_not_called()
        
    @patch('staff.views.requests.get')
    def test_edit_auth_service_unavailable(self, mock_requests_get):
        """
        If the auth service is unavailable (ConnectionError),
        returns 503 with appropriate JSON message.
        """
        
        request = self.factory.get(self.url)
        # Simulate 'jwt_token' existing
        request.COOKIES['jwt_token'] = 'test-jwt'

        # Raise a ConnectionError to simulate auth service outage
        mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection lost")
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"error": "Auth service unavailable: Connection lost"}
        )
        
    @patch('staff.views.requests.get')
    def test_edit_other_exceptions(self, mock_requests_get):
        """
        If some other unexpected exception is raised,
        returns 500 with the exception message.
        """
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'

        mock_requests_get.side_effect = Exception("Unexpected Error")
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {"error": "Unexpected Error"}
        )

    @patch('staff.views.requests.get')
    def test_edit_invalid_staff(self, mock_requests_get):
        """
        If the auth check (requests.get) returns non-200 status_code (e.g. 403),
        the view should return an unauthorized JSON response with that status.
        """
        request = self.factory.get(self.url)
        request.COOKIES['jwt_token'] = 'test-jwt'

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_requests_get.return_value = mock_response
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(
            response.content,
            {"error": "Unauthorized or forbidden access"}
        )

    @patch('staff.views.Reksadana')  # or wherever Reksadana is imported
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    @patch('staff.views.requests.get')
    def test_edit_get_request(self, mock_requests_get,
                              mock_get_categories, mock_get_banks, mock_reksadana):
        """
        If request.method == 'GET' and staff is authenticated (status_code=200),
        render 'edit_reksadana.html' with proper context.
        """
        request = self.factory.get(self.url, {'reksadana_id': '123'})
        request.COOKIES['jwt_token'] = 'test-jwt'

        # Simulate a 200 (staff OK)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Mock objects.get(...) return value
        mock_reksadana.objects.get.return_value = MagicMock()
        mock_get_categories.return_value = [{'id': 1, 'name': 'CategoryA'}]
        mock_get_banks.return_value = [{'id': 10, 'name': 'BankX'}]

        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BankX', response.content)      
        self.assertIn(b'CategoryA', response.content)  
        mock_requests_get.assert_called_once()
        mock_get_categories.assert_called_once()
        mock_get_banks.assert_called_once()

    @patch('staff.views.edit_reksadana')
    @patch('staff.views.requests.get')
    def test_edit_post_request_success(self, mock_requests_get, mock_edit_reksadana):
        """
        If request.method == 'POST' and edit_reksadana() returns status_code=201,
        the view should redirect to '/staff/dashboard/'.
        """
        request = self.factory.post(self.url, {'some': 'data'})
        request.COOKIES['jwt_token'] = 'test-jwt'

        # Mock the staff auth success
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_requests_get.return_value = mock_auth_response

        # Mock the edit_reksadana() function success
        mock_edit_response = MagicMock()
        mock_edit_response.status_code = 201
        mock_edit_reksadana.return_value = mock_edit_response

        response = edit_reksadana_staff(request)

        # Check for redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/staff/dashboard/')

    @patch('staff.views.Reksadana')  # Mock your DB access
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    @patch('staff.views.edit_reksadana')
    @patch('staff.views.requests.get')
    def test_edit_post_request_failed(self, mock_requests_get, mock_edit_reksadana,
                                      mock_get_categories, mock_get_banks, mock_reksadana):
        """
        If request.method == 'POST' but edit_reksadana() doesn't return 201,
        the view should render 'edit_reksadana.html' with the error context.
        """
        request = self.factory.post(self.url, {
            'reksadana_id': '123',
        })
        request.COOKIES['jwt_token'] = 'test-jwt'

        # Staff auth success
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_requests_get.return_value = mock_auth_response

        # edit_reksadana() fails -> e.g. 400 or 500
        mock_edit_response = MagicMock()
        mock_edit_response.status_code = 400
        mock_edit_response.content = json.dumps({"error": "Something went wrong"}).encode()
        mock_edit_reksadana.return_value = mock_edit_response

        # Mock Reksadana.objects.get, categories, banks
        mock_reksadana.objects.get.return_value = MagicMock()
        mock_get_categories.return_value = [{'id': 1, 'name': 'CategoryA'}]
        mock_get_banks.return_value = [{'id': 10, 'name': 'BankX'}]

        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 200)
        
        self.assertIn(b'error', response.content)
        self.assertIn(b'BankX', response.content)      
        self.assertIn(b'CategoryA', response.content)  
        mock_requests_get.assert_called_once()
        mock_get_categories.assert_called_once()
        mock_get_banks.assert_called_once()
    