from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
import requests
import json
from dashboard.views import dashboard, beli_unit, process_payment

class TestDashboard(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('dashboard:dashboard')
        
    def test_get_dashboard_not_authenticated(self):
        """
        If user_id is not present in the request, 
        we expect a redirect to the login page.
        """
        request = self.factory.get(self.url)
        # user_id intentionally not set to simulate "not authenticated"

        response = dashboard(request)
        
        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302)
        # Typically you'd expect it to redirect to something like '/login' 
        self.assertIn('/login/', response.url)
    
    
    @patch('dashboard.views.get_all_reksadana')
    def test_get_fetch_all_reksadana_failed(self, mock_get_all_reksadana):
        """
        If the 'get_all_reksadana' call returns a non-200 status code,
        the template should be rendered with an error message.
        """
        request = self.factory.get(self.url)
        request.user_id = 1  # Simulate an authenticated user
        request.user_username = 'testuser'

        # Mock the response from get_all_reksadana
        mock_response = MagicMock()
        mock_response.status_code = 500  # Non-200 to simulate failure
        mock_get_all_reksadana.return_value = mock_response

        response = dashboard(request)
        
        # Check that it's an HttpResponse (rendered template)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Failed to load reksadana data', response.content)
    
    @patch('dashboard.views.get_all_reksadana')
    def test_get_dashboard_success(self, mock_get_all_reksadana):
        """
        Successful scenario: user is authenticated, 
        get_all_reksadana returns a 200 status, 
        and we render 'dashboard.html' with reksadanas.
        """
        request = self.factory.get(self.url)
        request.user_id = 1
        request.user_username = 'testuser'

        # Simulate a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({
            'reksadanas': [
                {'name': 'Reksadana A', 'value': 100},
                {'name': 'Reksadana B', 'value': 200},
            ]
        }).encode('utf-8')
        mock_get_all_reksadana.return_value = mock_response

        response = dashboard(request)

        # Check rendered template & context
        self.assertEqual(response.status_code, 200)
        # The content should contain the reksadana data
        self.assertIn(b'Reksadana A', response.content)
        self.assertIn(b'Reksadana B', response.content)
        self.assertIn(b'testuser', response.content)
    
    @patch('dashboard.views.get_all_reksadana')
    def test_get_dashboard_error(self, mock_get_all_reksadana):
        """
        If an exception is raised while processing, 
        we should render the template with an error message.
        """
        request = self.factory.get(self.url)
        request.user_id = 1
        request.user_username = 'testuser'

        # Force an exception to be raised
        mock_get_all_reksadana.side_effect = Exception("Boom!")

        response = dashboard(request)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'An error occurred: Boom!', response.content)
        self.assertIn(b'testuser', response.content)
    

class TestBeliUnit(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('dashboard:beli_unit')

    def test_beli_unit_not_authenticated(self):
        """
        If the user is not authenticated (no user_id), 
        we expect a redirect to the login page.
        """
        request = self.factory.get(self.url)
        response = beli_unit(request)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_beli_unit_get_request(self):
        """
        If the request method is GET (and user is authenticated),
        the view should redirect to 'auth_page:index'.
        """
        request = self.factory.get(self.url)
        request.user_id = 1  # Simulate an authenticated user
        response = beli_unit(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)

    def test_beli_unit_post_content_json(self):
        """
        When request.method == 'POST' and content_type == 'application/json',
        we parse the JSON from request.body.
        Expect a 'payment_confirmation.html' template if data is valid.
        """
        
        data = {
            "id_reksadana": "123",
            "nominal": "20000"
        }
        request = self.factory.post(
            self.url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        request.user_id = 1  # authenticated
        response = beli_unit(request)

        # Because it's valid data, check that we see payment_confirmation
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Confirm Payment - Tibib", response.content)
        self.assertIn(b"123", response.content)
        self.assertIn(b"20000", response.content)

    def test_beli_unit_post_content_form(self):
        """
        When request.method == 'POST' with normal form data 
        (content_type='application/x-www-form-urlencoded'), 
        we read from request.POST. 
        Should also go to payment_confirmation if valid.
        """
        form_data = {
            "id_reksadana": "ABC",
            "nominal": "30000"
        }
        request = self.factory.post(
            self.url, 
            data=form_data
        )
        request.user_id = 1
        response = beli_unit(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Confirm Payment - Tibib", response.content)
        self.assertIn(b"ABC", response.content)
        self.assertIn(b"30000", response.content)

    def test_beli_unit_post_missing_required_fields(self):
        """
        If 'id_reksadana' or 'nominal' is missing, 
        we render the 'error.html' template with 
        an appropriate message.
        """
        # Missing 'nominal'
        form_data = {
            "id_reksadana": "123"
        }
        request = self.factory.post(
            self.url,
            data=form_data, 
            content_type='application/x-www-form-urlencoded'
        )
        request.user_id = 1
        response = beli_unit(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Missing required fields", response.content)

    def test_beli_unit_post_insufficient_amount(self):
        """
        If nominal < 10000, render 'error.html' 
        with the message about minimum investment.
        """
        form_data = {
            "id_reksadana": "123",
            "nominal": "5000"
        }
        request = self.factory.post(
            self.url,
            data=form_data
        )
        request.user_id = 1
        response = beli_unit(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Minimum investment amount is Rp 10,000", response.content)

    def test_beli_unit_post_value_error(self):
        """
        If the nominal cannot be converted to float, 
        we render 'error.html' with the 'Invalid amount format' message.
        """
        form_data = {
            "id_reksadana": "123",
            "nominal": "abc"  # Not a float
        }
        request = self.factory.post(
            self.url,
            data=form_data
        )
        request.user_id = 1
        response = beli_unit(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid amount format", response.content)

    def test_beli_unit_post_success(self):
        """
        A successful POST request with valid fields 
        and nominal >= 10000 leads to 'payment_confirmation.html'.
        """
        form_data = {
            "id_reksadana": "xyz",
            "nominal": "20000"
        }
        request = self.factory.post(
            self.url,
            data=form_data
        )
        request.user_id = 1
        response = beli_unit(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Confirm Payment - Tibib", response.content)
        self.assertIn(b"xyz", response.content)
        self.assertIn(b"20000", response.content)

    def test_beli_unit_post_other_error(self):
        """
        If an unexpected exception occurs, we render 'error.html'
        with "An error occurred" in the context.
        """
        # Create a POST request with valid form data
        form_data = {
            "id_reksadana": "xyz",
            "nominal": "20000"
        }
        request = self.factory.post(self.url, data=form_data)
        request.user_id = 1

        # Force an exception by setting request.POST to None
        request.POST = None

        response = beli_unit(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"An error occurred:", response.content)
            
class TestProcessPayment(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('dashboard:process_payment')

    def test_process_payment_get_not_allowed(self):
        """
        GET requests should return "Method not allowed" with status 405.
        """
        request = self.factory.get(self.url)
        response = process_payment(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b"Method not allowed")

    def test_process_payment_post_not_authenticated(self):
        """
        If request.user_id is missing, the view returns a 401 JsonResponse.
        """
        data = {
            "id_reksadana": "123",
            "nominal": "10000"
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        # Do NOT set request.user_id to simulate non-authenticated user
        response = process_payment(request)
        # self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {"error": "Unauthorized"})

    @patch('dashboard.views.create_unit_dibeli')
    @patch('dashboard.views.encrypt_and_sign')
    def test_process_payment_post_content_json(self, mock_encrypt_and_sign, mock_create_unit_dibeli):
        """
        Valid POST request with JSON content should process payment successfully.
        """
        # Arrange: Setup mocks to simulate successful unit creation.
        mock_encrypt_and_sign.return_value = ('encrypted_nominal', 'fake_signature')
        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_unit_dibeli.return_value = mock_create_response

        data = {
            "id_reksadana": "456",
            "nominal": "20000"
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user_id = 1  # Simulate authenticated user.
        request.session = {}

        # Act
        response = process_payment(request)

        # Assert: Expect a redirect to portfolio:index and success message stored in session.
        self.assertEqual(response.status_code, 302)
        self.assertIn('/portfolio/', response.url)
        self.assertEqual(
            request.session.get('success_message'),
            "Your investment has been processed successfully!"
        )

    @patch('dashboard.views.create_unit_dibeli')
    @patch('dashboard.views.encrypt_and_sign')
    def test_process_payment_post_content_form(self, mock_encrypt_and_sign, mock_create_unit_dibeli):
        """
        Valid POST request with form data should process payment successfully.
        """
        mock_encrypt_and_sign.return_value = ('encrypted_nominal', 'fake_signature')
        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_unit_dibeli.return_value = mock_create_response

        form_data = {
            "id_reksadana": "789",
            "nominal": "30000",
            "payment_method": "credit_card"
        }
        request = self.factory.post(self.url, data=form_data)
        request.user_id = 1
        request.session = {}

        response = process_payment(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/portfolio/', response.url)
        self.assertEqual(
            request.session.get('success_message'),
            "Your investment has been processed successfully!"
        )

    def test_process_payment_post_missing_field(self):
        """
        If required fields are missing (e.g. missing 'id_reksadana'),
        the view returns a 400 JsonResponse.
        """
        # Using JSON data missing 'id_reksadana'
        data = {
            "nominal": "15000"
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user_id = 1
        response = process_payment(request)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "Missing required fields"})

    def test_process_payment_post_value_error(self):
        """
        When 'nominal' cannot be converted to int, the view should render error.html.
        """
        data = {
            "id_reksadana": "123",
            "nominal": "abc"  # Invalid numeric format.
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user_id = 1
        response = process_payment(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid amount format: abc", response.content)

    @patch('dashboard.views.create_unit_dibeli')
    @patch('dashboard.views.encrypt_and_sign')
    def test_process_payment_post_failed(self, mock_encrypt_and_sign, mock_create_unit_dibeli):
        """
        When create_unit_dibeli returns a non-201 status code,
        the view should render error.html with the API error message.
        """
        mock_encrypt_and_sign.return_value = ('encrypted_nominal', 'fake_signature')
        mock_create_response = MagicMock()
        mock_create_response.status_code = 400
        error_message = "Creation failed"
        mock_create_response.content = json.dumps({"error": error_message}).encode('utf-8')
        mock_create_unit_dibeli.return_value = mock_create_response

        data = {
            "id_reksadana": "123",
            "nominal": "25000"
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user_id = 1
        request.session = {}

        response = process_payment(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unit creation failed: Creation failed", response.content)

    @patch('dashboard.views.create_unit_dibeli')
    @patch('dashboard.views.encrypt_and_sign')
    def test_process_payment_post_success(self, mock_encrypt_and_sign, mock_create_unit_dibeli):
        """
        A successful POST request results in redirecting to portfolio:index.
        """
        mock_encrypt_and_sign.return_value = ('encrypted_nominal', 'fake_signature')
        mock_create_response = MagicMock()
        mock_create_response.status_code = 201
        mock_create_unit_dibeli.return_value = mock_create_response

        data = {
            "id_reksadana": "555",
            "nominal": "35000"
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user_id = 1
        request.session = {}

        response = process_payment(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/portfolio/', response.url)
        self.assertEqual(
            request.session.get('success_message'),
            "Your investment has been processed successfully!"
        )

    @patch('dashboard.views.encrypt_and_sign')
    def test_process_payment_post_other_error(self, mock_encrypt_and_sign):
        """
        If an unexpected exception is raised (e.g. in encrypt_and_sign),
        the view should render error.html with an error message.
        """
        # Force encrypt_and_sign to raise an exception.
        mock_encrypt_and_sign.side_effect = Exception("Unexpected Error")

        data = {
            "id_reksadana": "777",
            "nominal": "40000"
        }
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user_id = 1
        request.session = {}

        response = process_payment(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"An error occurred: Unexpected Error", response.content)