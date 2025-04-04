from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
import requests
import json

from reksadana_rest.models import Reksadana
from staff.views import show_dashboard, create_reksadana_staff, edit_reksadana_staff

class TestShowDashboard(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:dashboard_admin')  
    
    def test_show_dashboard_unauthorized_role(self):
        """
        If user_role != staff, returns 403.
        """
        request = self.factory.get(self.url)
        request.user_role = "user"
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Forbidden:", response.content)
        
    @patch('staff.views.fetch_all_reksadanas')
    def test_show_dashboard_get_request_exception(self, mock_fetch_all):
        """
        If requests.get raises an exception on a GET request,
        """
        mock_fetch_all.return_value = Exception("Some GET error")
        
        request = self.factory.get(self.url)
        request.user_role = "staff"
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Internal Server Error', response.content)
        
    # Valid Staff
    @patch('staff.views.fetch_all_reksadanas')
    def test_show_dashboard_valid_staff(self, mock_fetch_all):
        """
        If requests.get to /staff/ returns 200, the method should:
          - Call fetch_all_reksadanas()
          - Render 'dashboard_admin.html'
          - Pass the reksadanas in context
        """

        # Mock fetch_all_reksadanas return value
        mock_fetch_all.return_value = [
            {'id': 1, 'name': 'Some Reksadana'},
            {'id': 2, 'name': 'Another Reksadana'}
        ]

        request = self.factory.get(self.url)
        request.user_role = "staff"
        
        response = show_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Some Reksadana', response.content)
        self.assertIn(b'Another Reksadana', response.content)
        mock_fetch_all.assert_called_once()


class TestCreateReksadanaStaff(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:create_reksadana')  

    def test_create_reksadana_unauthorized_role(self):
        """
        If user_role != staff, returns 403.
        """
        request = self.factory.get(self.url)
        request.user_role = "user"
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Forbidden:", response.content)
        
    @patch('staff.views.create_reksadana')
    def test_post_create_reksadana_success(self, mock_create_reksadana):
        """
        If create_reksadana returns a response with status code 201,
        the view should redirect to '/staff/dashboard/'.
        """
        # Create a fake response that simulates a successful creation.
        fake_response = MagicMock()
        fake_response.status_code = 201
        mock_create_reksadana.return_value = fake_response

        # Simulate a POST request from a staff user.
        request = self.factory.post(self.url)
        request.user_role = "staff"

        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/staff/dashboard/')
        
    @patch('staff.views.handle_error')
    @patch('staff.views.create_reksadana')
    def test_post_create_reksadana_error_response(self, mock_create_reksadana, mock_handle_error):
        """
        If create_reksadana returns a response with a non-201 status code,
        the view should call handle_error with the error message from the response.
        """
        # Set up a fake response from create_reksadana
        fake_response = MagicMock()
        fake_response.status_code = 400
        error_message = "Test error message"
        fake_response.content = json.dumps({"error": error_message}).encode('utf-8')
        mock_create_reksadana.return_value = fake_response

        # Set up handle_error to return a fake error HttpResponse
        fake_handle_error_response = MagicMock()
        fake_handle_error_response.status_code = 400
        fake_handle_error_response.content = f"Error: {error_message}".encode('utf-8')
        mock_handle_error.return_value = fake_handle_error_response

        request = self.factory.post(self.url)
        request.user_role = "staff"

        response = create_reksadana_staff(request)

        # Assert that handle_error was called with the correct parameters
        mock_handle_error.assert_called_once_with(
            request,
            400,
            error_message,
            back_url='/staff/create_reksadana/'
        )

        # Verify the response from the view is as expected.
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Error: Test error message", response.content)
        
    @patch('json.loads')
    def test_post_create_reksadana_json_decode_error(self, mock_decode_json):
        """
        If error when decoding json, raises an exception, returns 500
        """
        mock_decode_json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        
        request = self.factory.post(self.url)
        request.user_role = "staff"
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Invalid server response format', response.content)
   
    @patch('staff.views.create_reksadana')
    def test_post_create_reksadana_other_error(self, mock_create_reksadana):
        """
        If a generic exception occurs during POST, it should be caught by the
        second exception handler and return a 500 with a 'Server Error: ...' message.
        """
        request = self.factory.post(self.url)
        request.user_role = "staff"
        
        mock_create_reksadana.side_effect=Exception("Some Error")
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"Server Error: Some Error", response.content)
        
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    def test_get_create_reksadana_form_success(self, mock_get_categories, mock_get_banks):
        """
        If is valid staff, and get_all_banks and get_all_categories, 
        render the create_reksadana.html form
        """
        # Setup mocks
        mock_get_categories.return_value = [{'id': 1, 'name': 'CategoryA'}]
        mock_get_banks.return_value = [{'id': 10, 'name': 'BankX'}]
        
        request = self.factory.get(self.url)
        request.user_role = "staff"
        
        response = create_reksadana_staff(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BankX', response.content)      
        self.assertIn(b'CategoryA', response.content) 
        mock_get_categories.assert_called_once()
        mock_get_banks.assert_called_once()
        
        
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    def test_get_create_reksadana_failed_fetch_all(self, mock_get_categories, mock_get_banks):
        """
        If is valid staff, but get_all_banks or get_all_categories has error, 
        we expect to return a 500 with a 'Failed to load form: ...' message..
        """
        # Setup mocks
        mock_get_categories.side_effect = Exception("Test failure")
        mock_get_banks.side_effect = Exception("Test failure")

        request = self.factory.get(self.url)
        request.user_role = "staff"
        
        response = create_reksadana_staff(request)
        
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Failed to load form', response.content)
        mock_get_categories.assert_called_once()
        # Since get_all_categories fails, get_all_banks should not be called.
        mock_get_banks.assert_not_called()
        
class TestEditReksadanaStaff(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('staff:edit_reksadana')  
        
    def test_edit_reksadana_unauthorized_role(self):
        """
        If user_role != staff, returns 403.
        """
        request = self.factory.get(self.url)
        request.user_role = "user"
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Forbidden:", response.content)
        
    def test_edit_reksadana_product_id_missing(self):
        """
        If reksadana_id missing, return error 400
        """
        
        request = self.factory.get(self.url)
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Bad Request: Missing investment product ID', response.content)
        
    @patch('staff.views.Reksadana.objects.get')
    def test_edit_reksadana_product_not_found(self, mock_get):
        """
        If Reksadana.objects.get raises DoesNotExist, the view should return a 404
        with "Investment product not found" in the response.
        """
        mock_get.side_effect = Reksadana.DoesNotExist("Not found")
        request = self.factory.get(self.url, {'reksadana_id': '1'})
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request) 

        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Investment product not found", response.content)
        
    def test_edit_reksadana_product_id_format_invalid(self):
        """
        If Reksadana.objects.get raises ValidationError for product ID format, the view should return a 400
        with "Invalid product ID format" in the response.
        """
        request = self.factory.get(self.url, {'reksadana_id': 'abc'})
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request) 

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid product ID format", response.content)
        
    @patch('staff.views.edit_reksadana')
    @patch('staff.views.Reksadana.objects.get')
    def test_post_edit_reksadana_success(self, mock_get, mock_edit_reksadana):
        """
        If edit_reksadana returns a response with status code 200,
        the view should redirect to '/staff/dashboard/'.
        """
        # Create a fake response that simulates a successful edit.
        fake_response = MagicMock()
        fake_response.status_code = 200
        mock_edit_reksadana.return_value = fake_response
        
        # Return a dummy Reksadana instance.
        dummy_uuid = "123e4567-e89b-12d3-a456-426614174000"
        dummy_reksadana = MagicMock()
        dummy_reksadana.id_reksadana = dummy_uuid
        mock_get.return_value = dummy_reksadana

        # Simulate a POST request from a staff user.
        request = self.factory.post(self.url, {'reksadana_id': dummy_uuid})
        request.user_role = "staff"

        response = edit_reksadana_staff(request)
        # self.assertIn(b"Invalid product sbsbsbsb", response.content)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/staff/dashboard/')
        
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    @patch('staff.views.Reksadana.objects.get')
    def test_get_edit_reksadana_success(self, mock_get_reksadana, mock_get_categories, mock_get_banks):
        """
        If is valid staff, but get_all_categories fails,
        we expect to return a 500 with a 'Failed to load edit form: ...' message.
        """
        
        # Setup mocks
        mock_get_categories.return_value = [{'id': 1, 'name': 'CategoryA'}]
        mock_get_banks.return_value = [{'id': 10, 'name': 'BankX'}]
        dummy_uuid = "123e4567-e89b-12d3-a456-426614174000"
        dummy_reksadana = MagicMock()
        dummy_reksadana.id_reksadana = dummy_uuid
        mock_get_reksadana.return_value = dummy_reksadana

        # Simulate a POST request from a staff user.
        request = self.factory.get(self.url, {'reksadana_id': dummy_uuid})
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BankX', response.content)      
        self.assertIn(b'CategoryA', response.content) 
        mock_get_reksadana.assert_called_once()
        mock_get_categories.assert_called_once()
        mock_get_banks.assert_called_once()
        
    @patch('staff.views.Reksadana.objects.get')
    @patch('json.loads')
    def test_post_edit_reksadana_json_decode_error(self, mock_decode_json, mock_get_reksadana):
        """
        If error when decoding json, raises an exception, returns 500
        """
        dummy_uuid = "123e4567-e89b-12d3-a456-426614174000"
        dummy_reksadana = MagicMock()
        dummy_reksadana.id_reksadana = dummy_uuid
        mock_get_reksadana.return_value = dummy_reksadana
        
        mock_decode_json.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)
        
        # Simulate a POST request with valid staff
        request = self.factory.post(self.url, {'reksadana_id': dummy_uuid})
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Invalid server response format', response.content)
        
    @patch('staff.views.Reksadana.objects.get')
    @patch('staff.views.edit_reksadana')
    def test_post_edit_reksadana_other_exception(self, mock_response, mock_get_reksadana):
        """
        If other error occurs when post request, returns 500
        """
        dummy_uuid = "123e4567-e89b-12d3-a456-426614174000"
        dummy_reksadana = MagicMock()
        dummy_reksadana.id_reksadana = dummy_uuid
        mock_get_reksadana.return_value = dummy_reksadana
        
        mock_response.return_value = Exception("Some Server Error")
        
        # Simulate a POST request with valid staff
        request = self.factory.post(self.url, {'reksadana_id': dummy_uuid})
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request)
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Server Error:', response.content)
        
    @patch('staff.views.get_all_banks')
    @patch('staff.views.get_all_categories')
    @patch('staff.views.Reksadana.objects.get')
    def test_get_edit_reksadana_failed_fetch(self, mock_get_reksadana, mock_get_categories, mock_get_banks):
        """
        If is valid staff, but get_all_categories fails,
        we expect to return a 500 with a 'Failed to load edit form: ...' message.
        """
        # Let the reksadana lookup succeed.
        dummy_reksadana = MagicMock()
        dummy_reksadana.id_reksadana = "123e4567-e89b-12d3-a456-426614174000"
        mock_get_reksadana.return_value = dummy_reksadana

        # Simulate an error in fetching categories.
        mock_get_categories.side_effect = Exception("Test failure")
        # Optionally, have get_all_banks return a dummy value (it won't be called if get_all_categories fails)
        mock_get_banks.return_value = ["dummy bank"]

        request = self.factory.get(self.url, {'reksadana_id': dummy_reksadana.id_reksadana})
        request.user_role = "staff"
        
        response = edit_reksadana_staff(request)
        
        # Force rendering if needed:
        if hasattr(response, 'render'):
            response.render()

        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Failed to load edit form: Test failure', response.content)
        mock_get_reksadana.assert_called_once()
        mock_get_categories.assert_called_once()
        # Since get_all_categories fails, get_all_banks should not be called.
        mock_get_banks.assert_not_called()
        
    @patch('staff.views.Reksadana.objects.get')
    @patch('staff.views.handle_error')
    @patch('staff.views.edit_reksadana')
    def test_post_edit_reksadana_error_response(self, mock_edit_reksadana, mock_handle_error, mock_get_reksadana):
        """
        If edit_reksadana returns a response with a non-200 status code,
        the view should call handle_error with the error message from the response.
        """
        # Set up a fake response from edit_reksadana
        fake_response = MagicMock()
        fake_response.status_code = 400
        error_message = "Test error message"
        fake_response.content = json.dumps({"error": error_message}).encode('utf-8')
        mock_edit_reksadana.return_value = fake_response

        # Set up handle_error to return a fake error HttpResponse
        fake_handle_error_response = MagicMock()
        fake_handle_error_response.status_code = 400
        fake_handle_error_response.content = f"Error: {error_message}".encode('utf-8')
        mock_handle_error.return_value = fake_handle_error_response
        
        dummy_uuid = "123e4567-e89b-12d3-a456-426614174000"
        dummy_reksadana = MagicMock()
        dummy_reksadana.id_reksadana = dummy_uuid
        mock_get_reksadana.return_value = dummy_reksadana
        
        # Simulate a POST request with valid staff
        request = self.factory.post(self.url, {'reksadana_id': dummy_uuid})
        request.user_role = "staff"

        response = edit_reksadana_staff(request)

        # Assert that handle_error was called with the correct parameters
        mock_handle_error.assert_called_once_with(
            request,
            400,
            error_message,
            back_url=f'/staff/edit_reksadana/?reksadana_id={dummy_uuid}'
        )

        # Verify the response from the view is as expected.
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Error: Test error message", response.content)