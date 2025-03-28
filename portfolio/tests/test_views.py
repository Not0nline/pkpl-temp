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
from reksadana_rest.models import Reksadana, CategoryReksadana, Bank, UnitDibeli

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
        
        self.assertEqual(response.status_code, 200)

    def test_index_invalid_method(self):
        request = MockRequest()
        request.method = 'POST'
        request.user_id = 1
        response = index(request)
        
        self.assertEqual(response.status_code, 405)

    @patch('reksadana_rest.views.delete_unit_dibeli_by_id')
    def test_process_sell_unauthorized(self, mock_delete):
        # Create request without user_id
        request = MockRequest(method='POST', body=json.dumps({}))
        
        response = process_sell(request)
        self.assertEqual(response.status_code, 401)
        mock_delete.assert_not_called()

    def test_process_jual_invalid(self):
        unit = UnitDibeli.objects.create(
            user_id = "00000000-0000-0000-0000-000000000001",
            id_reksadana = self.reksadana,
            nominal = 10000,
            waktu_pembelian = datetime.datetime.now()
        )
        valid_data = {
            'id_unitdibeli':unit.id
        }
        request = MockRequest(method='GET', body=json.dumps(valid_data), post_data=valid_data, user_id=1)
        p = process_sell(request)
        self.assertEquals(p.status_code,405)