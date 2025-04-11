import json
import base64
import os
import datetime
import django
from django.test import TestCase
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import MagicMock, patch, Mock
from portfolio.views import *
from reksadana_rest.models import Reksadana, CategoryReksadana, Bank, UnitDibeli
from django.contrib.messages.storage.fallback import FallbackStorage

class MockSession():
    
    def __init__(self):
        self._modified = False
        self._data = {}
    
    @property
    def modified(self):
        return self._modified
    
    @modified.setter
    def modified(self, value):
        self._modified = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._modified = True
        self._data[key] = value
    
    def __contains__(self, key):
        return key in self._data
    
    def __delitem__(self,key):
        return

class MockRequest():
    def __init__(self, method='POST', body=None, user_id=None, post_data=None, session=None):
        self.method = method
        if user_id is not None:
            self.user_id = user_id 
        self.user_role = 'user'
        self._body = body.encode('utf-8') if body else b''
        self._post = post_data if post_data else {}
        self.META = {'CONTENT_TYPE': 'application/json', 'HTTP_AUTHORIZATION': None}
        self.session = session if session else {}
        self.COOKIES = {}

        self._messages = FallbackStorage(self)


    @property
    def body(self):
        return self._body

    @property
    def POST(self):
        return self._post

    # def set_post(self, post_data):
        # self._post = post_data

class PortfolioViewTests(TestCase):
    def setUp(self):
        # Create test data
        self.category = CategoryReksadana.objects.create(name="Equity Fund")
        self.kustodian = Bank.objects.create(name="Custodian Bank")
        self.penampung = Bank.objects.create(name="Receiving Bank")
        
        self.reksadana = Reksadana.objects.create(
            name='Test Reksadana',
            nav=1000.0,
            aum=0,
            tingkat_resiko='Konservatif',
            category=self.category,
            kustodian=self.kustodian,
            penampung=self.penampung
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    @patch('portfolio.views.get_units_by_user')
    def test_index_success_with_session_message(self, mock_get_units):
        # Mock successful units retrieval
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps([{"id": 1, "name": "Test Unit"}]).encode('utf-8')
        mock_get_units.return_value = mock_response

        # Create request with session message
        request = MockRequest(method='GET', user_id=1)
        request.session = MockSession()
        request.session['success_message']='success_message'

        # Call index view
        with patch('portfolio.views.render') as mock_render:
            index(request)
            
            # Assert render was called with correct context
            mock_render.assert_called_once()
            context = mock_render.call_args

            self.assertIn('success_message', str(context))

    @patch('portfolio.views.get_units_by_user')
    def test_index_failed_units_retrieval(self, mock_get_units):
        # Mock failed units retrieval
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = json.dumps({"error": "Retrieval Error"}).encode('utf-8')
        mock_get_units.return_value = mock_response

        # Create request
        request = MockRequest(method='GET', user_id=1)

        # Call index view
        with patch('portfolio.views.render') as mock_render:
            index(request)
            
            # Assert render was called with error context
            mock_render.assert_called_once()
            print('p2p',mock_render.call_args)

            self.assertIn('error', str(mock_render.call_args))

    def test_index_invalid_method(self):
        # Test POST method on index
        request = MockRequest(method='POST')
        response = index(request)
        
        self.assertEqual(response.status_code, 405)
    
    def test_index_invalid_user_role(self):
        request = MockRequest(method='GET')
        request.user_role = 'staff'
        response = index(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Forbidden',response.content)
        self.assertIn(b'403',response.content)

    @patch('portfolio.views.get_units_by_user')
    def test_index_random_error(self, mock_get):
        request = MockRequest(method='GET')
        response = index(request)
        mock_get.side_effect = Exception("Test Exception")
        self.assertIn('Error loading portfolio',str(response.content))

    
    @patch('reksadana_rest.views.delete_unit_dibeli_by_id')
    def test_jual_unitdibeli(self, mock_delete):
        unit = UnitDibeli.objects.create(
            user_id = "00000000-0000-0000-0000-000000000001",
            id_reksadana = self.reksadana,
            nominal = 10000,
            waktu_pembelian = datetime.datetime.now(),
            nav_dibeli = 1
        )
        mock = Mock()
        mock.status_code = 200
        mock_delete.return_value = mock

        base_url = "http://localhost:8000/"
        valid_data = {
            'id_unitdibeli':1
        }
        headers = {
            'Authorization': None,
            'Content-Type': 'application/json'
        }
        request = MockRequest(method='POST', post_data=valid_data, user_id=1)
        jual_unitdibeli(request)
    
    def test_jual_unitdibeli_invalid_user_role(self):
        request = MockRequest(method='GET')
        request.user_role = 'staff'
        response = jual_unitdibeli(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Forbidden',response.content)
        self.assertIn(b'403',response.content)

    @patch('portfolio.views.requests.post')
    def test_jual_unitdibeli_post_error(self, mock_post):
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(1)}, 
            user_id=1
        )
        request.user_id = 1
        request.user_role = 'user'
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        response = jual_unitdibeli(request)
        print('asaa',response.content)
        self.assertIn('Failed to retrieve card information',str(response.content))
    
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_get_unitdibeli_error(self, mock_get, mock_post):
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(1)}, 
            user_id=1
        )
        request.user_id = 1
        request.user_role = 'user'
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        mock_get.return_value = mock_response
        response = jual_unitdibeli(request)
        print('asaa',response.content)
        self.assertIn('Failed to retrieve card information',str(response.content))

    @patch('reksadana_rest.views.delete_unit_dibeli_by_id')
    def test_process_sell_success(self, mock_delete):
        # Create test unit
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now()
        )
        
        # Setup mock response from delete function
        mock_response = Mock()
        mock_response.status_code = 201  # Note: Your process_sell checks for 201
        mock_response.content = json.dumps({"message": "UnitDibeli deleted successfully"}).encode('utf-8')
        mock_delete.return_value = mock_response
        
        # Create request
        valid_data = {'id_unitdibeli': unit.id}
        request = MockRequest(
            method='POST',
            body=json.dumps(valid_data),
            post_data=valid_data,
            user_id="00000000-0000-0000-0000-000000000001"  # Match the unit's user_id
        )
        
        # Call the function
        response = process_sell(request)
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], "Successfully sold unit reksadana")
        mock_delete.assert_called_once()

    @patch('portfolio.views.decrypt_and_verify')
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.delete_unit_dibeli_by_id')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_success(self, mock_get, mock_delete, mock_post, mock_enc):
        # Mock successful delete

        mock_data = {
            "nav_dulu": 1000,
            "nav_sekarang": 2000,
            "total_beli": 500000
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(mock_data).encode('utf-8')
        mock_delete.return_value = mock_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(mock_data).encode('utf-8')
        mock_get.return_value = mock_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credit_card": 1, "signature": "****1234"}
        mock_post.return_value = mock_response

        mock_enc.return_value = "****1234"

        # Prepare test data
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now(),
            nav_dibeli =1
        )

        # Create request
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(unit.id)}, 
            user_id="00000000-0000-0000-0000-000000000001",
        )
        request.user_role = 'user'

        # Use patch to track messages
        with patch('portfolio.views.messages.success') as mock_messages:
            jual_unitdibeli(request)
            mock_messages.assert_called_once()

    def test_jual_unitdibeli_unauthorized(self):
        # Test unauthorized access
        request = MockRequest(method='POST')
        request.user_id = None

        # Use patch to track messages and redirect
        with patch('portfolio.views.messages') as mock_messages, \
             patch('portfolio.views.redirect') as mock_redirect:
            jual_unitdibeli(request)

            mock_messages.error.assert_called_once()
            mock_redirect.assert_called_once_with('auth_page:login')

    @patch('portfolio.views.decrypt_and_verify')
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.delete_unit_dibeli_by_id')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_exception(self, mock_get, mock_delete, mock_post, mock_enc):
        # Simulate an exception during delete
        mock_delete.side_effect = Exception("Test Exception")

        mock_data = {
            "nav_dulu": 1000,
            "nav_sekarang": 2000,
            "total_beli": 500000
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(mock_data).encode('utf-8')
        mock_get.return_value = mock_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credit_card": 1, "signature": "****1234"}
        mock_post.return_value = mock_response

        mock_enc.return_value = "****1234"

        # Prepare test data
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now(),
            nav_dibeli = 1
        )

        # Create request
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(unit.id)}, 
            user_id=1
        )
        request.user_role = 'user'

        # Use patch to track messages and redirect
        with patch('portfolio.views.messages') as mock_messages, \
             patch('portfolio.views.redirect') as mock_redirect:
            jual_unitdibeli(request)

            # Assert error message and redirect
            mock_messages.error.assert_called_once_with(request, "An error occurred: Test Exception")
            mock_redirect.assert_called_once_with('portfolio:index')

    def test_jual_unitdibeli_missing_unit_id(self):
        # Test missing unit ID
        request = MockRequest(method='POST', user_id=1)
        request._post = {}  # Ensure no unit ID

        # Use patch to track messages and redirect
        with patch('portfolio.views.messages') as mock_messages, \
             patch('portfolio.views.redirect') as mock_redirect:
            jual_unitdibeli(request)

            mock_messages.error.assert_called_once()
            mock_redirect.assert_called_once_with('portfolio:index')

    def test_jual_unitdibeli_invalid_method(self):
        # Test GET method
        request = MockRequest(method='GET', user_id=1)

        # Use patch to track messages and redirect
        with patch('portfolio.views.messages') as mock_messages, \
             patch('portfolio.views.redirect') as mock_redirect:
            jual_unitdibeli(request)

            mock_messages.error.assert_called_once()
            mock_redirect.assert_called_once_with('portfolio:index')

    @patch('portfolio.views.delete_unit_dibeli_by_id')
    def test_process_sell_success(self, mock_delete):
        # Mock successful delete
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.content = json.dumps({"message": "Success"}).encode('utf-8')
        mock_delete.return_value = mock_response

        # Prepare test data
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now(),
            nav_dibeli = 1
        )

        # Create request
        request = MockRequest(
            method='POST', 
            body=json.dumps({'id_unitdibeli': str(unit.id)}),
            user_id=1
        )

        # Call process_sell
        response = process_sell(request)
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], "Successfully sold unit reksadana")

    def test_process_sell_error_parsing(self):
        # Create request with invalid response content
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = b'Invalid JSON'

        # Patch delete_unit_dibeli_by_id to return mock response
        with patch('portfolio.views.delete_unit_dibeli_by_id') as mock_delete:
            mock_delete.return_value = mock_response

            # Create request
            request = MockRequest(
                method='POST', 
                body=json.dumps({'id_unitdibeli': '1'}),
                user_id=1
            )

            # Call process_sell
            response = process_sell(request)
            
            # Assertions
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.content)
            self.assertEqual(response_data['error'], 'Failed to sell unit')


    def test_process_sell_unauthorized(self):
        # Test unauthorized access
        request = MockRequest(method='POST')
        request.user_id = None

        response = process_sell(request)
        self.assertEqual(response.status_code, 401)
    
    def test_process_sell_invalid_user_role(self):
        # Test unauthorized access
        request = MockRequest(method='POST')
        request.user_id = 1
        request.user_role = 'staff'

        response = process_sell(request)
        self.assertEqual(response.status_code, 403)

    def test_process_sell_invalid_method(self):
        # Test GET method
        request = MockRequest(method='GET', user_id=1)

        response = process_sell(request)
        self.assertEqual(response.status_code, 405)

    def test_process_sell_invalid_body(self):
        # Test invalid request body
        request = MockRequest(method='POST', body='invalid json', user_id=1)

        response = process_sell(request)
        self.assertEqual(response.status_code, 400)

    def test_process_sell_missing_unit_id(self):
        # Test missing unit ID
        request = MockRequest(
            method='POST', 
            body=json.dumps({}),
            user_id=1
        )

        response = process_sell(request)
        self.assertEqual(response.status_code, 400)

    def test_index_request_with_session(self):
        # Create a mock request with session data
        request = MockRequest(method='GET')
        request.session = MockSession()
        request.session['success_message']='uwu'
        request.session['token']='uwu'
        request.session['user_id']=1
        
        request.user_role = 'user'

        # Patch get_units_by_user to return a successful response
        with patch('portfolio.views.get_units_by_user') as mock_get_units, \
             patch('portfolio.views.render') as mock_render:
            # Create a mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = json.dumps([{'id': 1}]).encode('utf-8')
            mock_get_units.return_value = mock_response

            # Call index view
            index(request)

            # Verify that request attributes are set correctly
            self.assertEqual(request.user_id, 1)

    def test_index_user_id_from_session(self):
        # Create a mock request with session data
        request = MockRequest(method='GET')
        request.session = {'user_id': 42}

        # Patch get_units_by_user to return a successful response
        with patch('portfolio.views.get_units_by_user') as mock_get_units, \
             patch('portfolio.views.render') as mock_render:
            # Create a mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = json.dumps([{'id': 1}]).encode('utf-8')
            mock_get_units.return_value = mock_response

            # Call index view
            index(request)

            # Verify that user_id was set from session
            self.assertEqual(request.user_id, 42)

    @patch('portfolio.views.decrypt_and_verify')
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.delete_unit_dibeli_by_id')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_error_message_parsing(self, mock_get, mock_delete, mock_post, mock_enc):
        # Mock a response with a specific error message
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = json.dumps({"error": "Specific sell error"}).encode('utf-8')
        mock_delete.return_value = mock_response

        mock_data = {
            "nav_dulu": 1000,
            "nav_sekarang": 2000,
            "total_beli": 500000
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(mock_data).encode('utf-8')
        mock_get.return_value = mock_response

        mock_enc.return_value = "****1234"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credit_card": 1, "signature": "****1234"}
        mock_post.return_value = mock_response

        # Prepare test data
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now(),
            nav_dibeli = 1
        )

        # Create request
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(unit.id)}, 
            user_id="00000000-0000-0000-0000-000000000001",
        )

        # Use patch to track messages and redirect
        with patch('portfolio.views.messages') as mock_messages, \
             patch('portfolio.views.redirect') as mock_redirect:
            jual_unitdibeli(request)

            # Assert specific error message from response
            mock_messages.error.assert_called_once_with(request, 'Specific sell error')
            mock_redirect.assert_called_once_with('portfolio:index')

    @patch('portfolio.views.decrypt_and_verify')
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.delete_unit_dibeli_by_id')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_json_decode_fail_delete(self, mock_get, mock_delete, mock_post, mock_enc):
        # Mock a response with a specific error message
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = json.dumps({}).encode('utf-16')
        mock_delete.return_value = mock_response

        mock_data = {
            "nav_dulu": 1000,
            "nav_sekarang": 2000,
            "total_beli": 500000
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(mock_data).encode('utf-8')
        mock_get.return_value = mock_response

        mock_enc.return_value = "****1234"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credit_card": 1, "signature": "****1234"}
        mock_post.return_value = mock_response

        # Prepare test data
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now(),
            nav_dibeli = 1
        )

        # Create request
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(unit.id)}, 
            user_id="00000000-0000-0000-0000-000000000001",
        )

        # Use patch to track messages and redirect
        with patch('portfolio.views.messages') as mock_messages, \
             patch('portfolio.views.redirect') as mock_redirect:
            jual_unitdibeli(request)

            # Assert specific error message from response
            mock_messages.error.assert_called_once_with(request, 'Failed to sell unit')
            mock_redirect.assert_called_once_with('portfolio:index')

    @patch('portfolio.views.decrypt_and_verify')
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_fail_get(self, mock_get, mock_post, mock_enc):
        mock_data = {
            "error": 1000,
            "nav_sekarang": 2000,
            "total_beli": 500000
        }

        mock_response2 = MagicMock()
        mock_response2.status_code = 400
        mock_response2.content = json.dumps(mock_data).encode('utf-8')
        mock_get.return_value = mock_response2

        mock_enc.return_value = "****1234"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credit_card": 1, "signature": "****1234"}
        mock_post.return_value = mock_response

        # Create request
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(1)}, 
            user_id="00000000-0000-0000-0000-000000000001",
        )
        request.user_role = 'user'

        r = jual_unitdibeli(request)
        self.assertIn('Selling units failed',str(r.content))

    @patch('portfolio.views.decrypt_and_verify')
    @patch('portfolio.views.requests.post')
    @patch('portfolio.views.delete_unit_dibeli_by_id')
    @patch('portfolio.views.get_unit_dibeli_by_id')
    def test_jual_unitdibeli_json_decode_fail_second_post(self, mock_get, mock_delete, mock_post, mock_enc):
        # Mock a response with a specific error message
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = json.dumps({}).encode('utf-16')
        mock_delete.return_value = mock_response

        mock_data = {
            "nav_dulu": 1000,
            "nav_sekarang": 2000,
            "total_beli": 500000
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = json.dumps(mock_data).encode('utf-8')
        mock_get.return_value = mock_response

        mock_enc.return_value = "****1234"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credit_card": 1, "signature": "****1234"}
        mock_post.return_value = mock_response

        mock_response3 = MagicMock()
        mock_response3.status_code = 400
        mock_response3.content = json.dumps(mock_data).encode('utf-8')
        mock_post.side_effect = [mock_response, mock_response3]


        # Prepare test data
        unit = UnitDibeli.objects.create(
            user_id="00000000-0000-0000-0000-000000000001",
            id_reksadana=self.reksadana,
            nominal=10000,
            waktu_pembelian=datetime.datetime.now(),
            nav_dibeli = 1
        )

        # Create request
        request = MockRequest(
            method='POST', 
            post_data={'id_unitdibeli': str(unit.id)}, 
            user_id="00000000-0000-0000-0000-000000000001",
        )
        r = jual_unitdibeli(request)
        self.assertIn('Payment failed',str(r.content))


    def test_process_sell_specific_error_message(self):
        # Create request with specific error response content
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content = json.dumps({"error": "Specific process sell error"}).encode('utf-8')

        # Patch delete_unit_dibeli_by_id to return mock response
        with patch('portfolio.views.delete_unit_dibeli_by_id') as mock_delete:
            mock_delete.return_value = mock_response

            # Create request
            request = MockRequest(
                method='POST', 
                body=json.dumps({'id_unitdibeli': '1'}),
                user_id=1
            )

            # Call process_sell
            response = process_sell(request)
            
            # Assertions
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.content)
            self.assertEqual(response_data['error'], 'Specific process sell error')

    def test_process_sell_unexpected_exception(self):
        # Create request that will raise an unexpected exception
        with patch('portfolio.views.delete_unit_dibeli_by_id') as mock_delete:
            # Simulate an unexpected exception
            mock_delete.side_effect = ValueError("Unexpected error")

            # Create request
            request = MockRequest(
                method='POST', 
                body=json.dumps({'id_unitdibeli': '1'}),
                user_id=1
            )

            # Call process_sell
            response = process_sell(request)
            
            # Assertions
            self.assertEqual(response.status_code, 500)
            response_data = json.loads(response.content)
            self.assertEqual(response_data['error'], 'Unexpected error')

    def test_index_invalid_json_response(self):
        """
        Test the index view when get_units_by_user returns non-JSON content
        """
        # Create a mock request
        request = MockRequest(method='GET', user_id=1)

        # Patch get_units_by_user to return an invalid JSON response
        with patch('portfolio.views.get_units_by_user') as mock_get_units, \
            patch('portfolio.views.render') as mock_render:
            # Create a mock response with invalid JSON
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'This is not valid JSON'
            mock_get_units.return_value = mock_response

            # Call index view
            index(request)
            
            # Verify render was called with the correct error context
            mock_render.assert_called_once()

            #TODO: masih salah assertnya
            self.assertIn('Invalid response format',str(mock_render.call_args))
            self.assertIn('\'units\': []',str(mock_render.call_args))