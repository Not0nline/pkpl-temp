# from django.test import SimpleTestCase
# from django.urls import resolve, reverse
# from reksadana_rest.views import *
# class TestUrls(SimpleTestCase):
#     def test_url_create_reksadana(self):
#         url = reverse("create_reksadana")
#         self.assertEqual(url, '/reksadana/create-reksadana/')
#         self.assertEqual(resolve(url).func, create_reksadana)

#     def test_url_get_all_reksadana(self):
#         url = reverse("get_all_reksadana")
#         self.assertEqual(url, '/reksadana/get-all-reksadana/')
#         self.assertEqual(resolve(url).func, get_all_reksadana)

#     def test_url_create_unit_dibeli(self):
#         url = reverse("create_unit_dibeli")
#         self.assertEqual(url, '/reksadana/create-unitdibeli/')
#         self.assertEqual(resolve(url).func, create_unit_dibeli)

#     def test_url_get_units_by_user(self):
#         url = reverse("get_units_by_user")
#         self.assertEqual(url, '/reksadana/get-unitdibeli-by-user/')
#         self.assertEqual(resolve(url).func, get_units_by_user)

#     def test_url_get_reksadana_history(self):
#         sample_uuid = '12345678-1234-5678-1234-567812345678'
#         url = reverse("get_reksadana_history", args=[sample_uuid])
#         self.assertEqual(url, f'/reksadana/get-reksadana-history/{sample_uuid}/')
#         self.assertEqual(resolve(url).func, get_reksadana_history)

#     def test_url_edit_reksadana(self):
#         url = reverse("edit_reksadana")
#         self.assertEqual(url, '/reksadana/edit-reksadana/')
#         self.assertEqual(resolve(url).func, edit_reksadana)