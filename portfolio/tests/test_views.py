import json
import base64
import os
import datetime
import django
from django.test import TestCase
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, Mock
from tibib.utils import encode_value
from portfolio.views import *
from reksadana_rest.models import Reksadana, CategoryReksadana, Bank

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

AES_KEY = base64.b64decode(os.getenv("AES_KEY"))
AES_IV = base64.b64decode(os.getenv("AES_IV"))

class MockRequest():
    def __init__(self, method='POST', body=None, user_id=None, post_data=None):
        super().__init__()
        self.method = method
        self.user_id = user_id
        self._body = body.encode('utf-8') if body else b''
        self._post = post_data if post_data else {}
        self.META = {'CONTENT_TYPE': 'application/json'}
        self.session={}
        self.COOKIES = {}

    @property
    def body(self):
        return self._body

    @property
    def POST(self):
        return self._post

    def set_post(self, post_data):
        self._post = post_data

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

        self.aes_key = AES_KEY
        self.aes_iv = AES_IV
    
    @patch('portfolio.views.render')
    def test_index(self, mock_render):
        mock_render.return_value = Mock(status_code=200)
        request = MockRequest()
        request.method = 'GET'
        request.user_id = 1
        response = index(request)
        
        mock_render.assert_called_once_with(
            request,
            'portfolio.html',  # Your template name
            context={'units': [], 'success_message': None} # Your expected context
        )
        
        self.assertEqual(response.status_code, 200)

    def test_index_invalid_method(self):
        request = MockRequest()
        request.method = 'POST'
        request.user_id = 1
        response = index(request)
        
        self.assertEqual(response.status_code, 405)
    
    @patch('requests.post')
    def test_jual_unitdibeli(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response

        base_url = "http://localhost:8000/"
        valid_data = {
            'id_unitdibeli':1
        }
        headers = {
            'Authorization': None,
            'Content-Type': 'application/json'
        }
        request = MockRequest(method='POST', post_data=valid_data)
        jual_unitdibeli(request)
        mock_post.assert_called_once_with(
            f"{base_url}/portfolio/process-sell/",
            json=valid_data,
            headers=headers
        )
    
    def test_process_jual(self):
        valid_data = {
            'id_unitdibeli':1
        }
        request = MockRequest(method='POST', post_data=valid_data)
        p  =process_sell(request)
        self.assertEquals(p.status_code, 201)

    def test_process_jual_invalid(self):
        valid_data = {
            'id_unitdibeli':1
        }
        headers = {
            'Authorization': None,
            'Content-Type': 'application/json'
        }
        request = MockRequest(method='GET', post_data=valid_data)
        p = process_sell(request)
        self.assertEquals(p,None)