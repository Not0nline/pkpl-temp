import json
import base64
import os
import datetime
import django
from django.test import TestCase
from django.http import HttpRequest, JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from tibib.utils import encode_value
from reksadana_rest.views import *
from reksadana_rest.models import Reksadana, CategoryReksadana, Bank, UnitDibeli, HistoryReksadana
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

    @property
    def body(self):
        return self._body

    @property
    def POST(self):
        return self._post

    def set_post(self, post_data):
        self._post = post_data

class ReksadanaViewTests(TestCase):
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
    

    # Test create_reksadana
    def test_create_reksadana_success(self):
        valid_data = {
            'name': 'New Reksadana',
            'nav': '1500',
            'category_id': self.category.id,
            'kustodian_id': self.kustodian.id,
            'penampung_id': self.penampung.id,
            'tingkat_resiko': 'Moderat'
        }
        request = MockRequest(method='POST', post_data=valid_data)
        response = create_reksadana(request)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', json.loads(response.content))

    def test_create_reksadana_missing_fields(self):
        invalid_data = {
            'name': '',  # Missing required name
            'nav': '1000',
            'category_id': self.category.id
        }
        request = MockRequest(method='POST', post_data=invalid_data)
        response = create_reksadana(request)
        self.assertEqual(response.status_code, 400)

    def test_create_reksadana_invalid_foreign_keys(self):
        invalid_data = {
            'name': 'Invalid Reksadana',
            'nav': '1000',
            'category_id': 9999,  # Invalid ID
            'kustodian_id': self.kustodian.id,
            'penampung_id': self.penampung.id,
            'tingkat_resiko': 'Konservatif'
        }
        request = MockRequest(method='POST', post_data=invalid_data)
        response = create_reksadana(request)
        self.assertEqual(response.status_code, 400)

    # Test edit_reksadana
    def test_edit_reksadana_success(self):
        edit_data = {
            'reksadana_id': self.reksadana.id_reksadana,
            'name': 'Updated Name',
            'category_id': self.category.id,
            'kustodian_id': self.kustodian.id,
            'penampung_id': self.penampung.id,
            'tingkat_resiko': 'Agresif'
        }
        request = MockRequest(method='POST', post_data=edit_data)
        response = edit_reksadana(request)
        self.assertEqual(response.status_code, 201)
        self.reksadana.refresh_from_db()
        self.assertEqual(self.reksadana.name, 'Updated Name')

    def test_edit_reksadana_not_found(self):
        edit_data = {
            'reksadana_id': 9999,  # Invalid ID
            'name': 'Updated Name',
            'category_id': self.category.id,
            'kustodian_id': self.kustodian.id,
            'penampung_id': self.penampung.id,
            'tingkat_resiko': 'Agresif'
        }
        request = MockRequest(method='POST', post_data=edit_data)
        response = edit_reksadana(request)
        self.assertEqual(response.status_code, 405)

    # Test get_all_reksadana
    def test_get_all_reksadana(self):
        request = MockRequest(method='GET')
        response = get_all_reksadana(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['reksadanas']), 1)

    # Test create_unit_dibeli
    def test_create_unit_dibeli_success(self):
        encrypted_nominal = encode_value('1000000')
        data = {
            'id_reksadana': str(self.reksadana.id_reksadana),
            'nominal': encrypted_nominal
        }
        request = MockRequest(method='POST', body=json.dumps(data), user_id=self.user.id)
        response = create_unit_dibeli(request)
        self.assertEqual(response.status_code, 201)

    def test_create_unit_dibeli_invalid_json(self):
        request = MockRequest(method='POST', body='invalid json', user_id=self.user.id)
        response = create_unit_dibeli(request)
        self.assertEqual(response.status_code, 400)

    def test_create_unit_dibeli_missing_fields(self):
        val = False
        try:
            data = {
                'id_reksadana': str(self.reksadana.id_reksadana)
                # Missing nominal
            }
            request = MockRequest(method='POST', body=json.dumps(data), user_id=self.user.id)
            response = create_unit_dibeli(request)
        except TypeError:
            val = True
        self.assertTrue(val)

    # Test get_units_by_user
    def test_get_units_by_user_authenticated(self):
        # Create a unit first
        UnitDibeli.objects.create(
            user_id=self.user.id,
            id_reksadana=self.reksadana,
            nominal=1000000,
            waktu_pembelian=datetime.datetime.now()
        )
        
        request = MockRequest(method='GET', user_id=self.user.id)
        response = get_units_by_user(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_get_units_by_user_unauthenticated(self):
        request = MockRequest(method='GET')
        response = get_units_by_user(request)
        self.assertEqual(response.status_code, 401)

    # Test get_reksadana_history
    def test_get_reksadana_history_success(self):
        request = MockRequest(method='GET')
        response = get_reksadana_history(request, self.reksadana.id_reksadana)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(len(data) > 0)

    def test_get_reksadana_history_not_found(self):
        request = MockRequest(method='GET')
        with self.assertRaises(Reksadana.DoesNotExist):
            get_reksadana_history(request, 9999)

    # Test delete_unit_dibeli_by_id
    def test_delete_unit_dibeli_success(self):
        unit = UnitDibeli.objects.create(
            user_id=self.user.id,
            id_reksadana=self.reksadana,
            nominal=1000000,
            waktu_pembelian=datetime.datetime.now()
        )
        
        data = {'id_unitdibeli': unit.id}
        print("data",unit.user_id, self.user.id)
        request = MockRequest(method='POST', body=json.dumps(data), user_id="00000000-0000-0000-0000-000000000001")
        response = delete_unit_dibeli_by_id(request)
        self.assertEqual(response.status_code, 200)

    def test_delete_unit_dibeli_unauthorized(self):
        unit = UnitDibeli.objects.create(
            user_id=self.user.id,
            id_reksadana=self.reksadana,
            nominal=1000000,
            waktu_pembelian=datetime.datetime.now()
        )
        
        data = {'id_unitdibeli': unit.id}
        request = MockRequest(method='POST', body=json.dumps(data), user_id=9999)  # Different user
        response = delete_unit_dibeli_by_id(request)
        self.assertEqual(response.status_code, 403)

    def test_delete_unit_dibeli_not_found(self):
        data = {'id_unitdibeli': 9999}
        request = MockRequest(method='POST', body=json.dumps(data), user_id=self.user.id)
        with self.assertRaises(django.http.response.Http404):
            delete_unit_dibeli_by_id(request)

    # Test get_all_categories
    def test_get_all_categories(self):
        request = MockRequest()
        categories = get_all_categories(request)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['name'], 'Equity Fund')

    # Test get_all_banks
    def test_get_all_banks(self):
        request = MockRequest()
        banks = get_all_banks(request)
        self.assertEqual(len(banks), 2)
        self.assertEqual(banks[0]['name'], 'Custodian Bank')
        self.assertEqual(banks[1]['name'], 'Receiving Bank')

    def test_create_reksadana_api_invalid_method(self):
        request = MockRequest(method='GET')
        response = create_reksadana_api(request)
        self.assertEqual(response.status_code, 405)


    # Test error cases
    def test_create_reksadana_server_error(self):
        # Simulate a server error by passing invalid data
        request = MockRequest(method='POST', post_data={'invalid': 'data'})
        response = create_reksadana(request)
        self.assertEqual(response.status_code, 400)

    def test_edit_reksadana_server_error(self):
        # Simulate a server error by passing invalid data
        request = MockRequest(method='POST', post_data={'invalid': 'data'})
        response = edit_reksadana(request)
        self.assertEqual(response.status_code, 400)