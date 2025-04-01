from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch, MagicMock
from dashboard.views import dashboard, beli_unit, process_payment
import json

class ViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_id = 1
        self.user_username = "testuser"

    @patch('reksadana_rest.views.get_all_reksadana')
    def test_dashboard_authenticated(self, mock_get_all_reksadana):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps({'reksadanas': [{'id': 1, 'name': 'Test Reksadana'}]}).encode()
        mock_get_all_reksadana.return_value = mock_response

        request = self.factory.get(reverse('auth_page:home'))
        request.user_id = "test_user"
        request.user_username = self.user_username

        response = dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Reksadana', response.content)
    
    def test_dashboard_redirects_when_not_authenticated(self):
        request = self.factory.get(reverse('auth_page:home'))
        response = dashboard(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('auth_page:login'))
    
    # def test_beli_unit_redirects_when_not_authenticated(self):
    #     request = self.factory.get(reverse('dashboard:beli_unit'))
    #     response = beli_unit(request)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, reverse('auth_page:login'))

    def test_beli_unit_invalid_amount(self):
        request = self.factory.post(reverse('dashboard:beli_unit'), {'id_reksadana': '1', 'nominal': 'abc'})
        request.user_id = self.user_id

        response = beli_unit(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid amount format', response.content)
    
    @patch('reksadana_rest.views.create_unit_dibeli')
    @patch('tibib.utils.encrypt_and_sign', return_value=("encrypted_nominal", "signature"))
    def test_process_payment_success(self, mock_encrypt, mock_create_unit):
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_create_unit.return_value = mock_response

        data = {
            'id_reksadana': 1,
            'nominal': '10000',
            'payment_method': 'bank_transfer'
        }
        request = self.factory.post(reverse('dashboard:process_payment'), json.dumps(data), content_type='application/json')
        request.user_id = self.user_id
        request.session = {}

        response = process_payment(request)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.url, reverse('portfolio:index'))
    
    # def test_process_payment_unauthorized(self):
    #     request = self.factory.post(reverse('dashboard:process_payment'))
    #     response = process_payment(request)
    #     self.assertEqual(response.status_code, 401)
    #     self.assertEqual(json.loads(response.content), {"error": "Unauthorized"})
