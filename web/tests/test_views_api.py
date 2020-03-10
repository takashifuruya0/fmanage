from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from web.models import AssetStatus, Stock
from datetime import date
import json


class APIViewTest(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        # self.client.force_login(user=self.u)
        self.stock1 = Stock.objects.create(
            code="1570", name="test1", market="market1", industry="industry", is_trust=False
        )
        self.stock2 = Stock.objects.create(
            code="8410", name="test2", market="market2", industry="industry", is_trust=False
        )
        self.stock3 = Stock.objects.create(
            code="2931113C", name="test3", market="market3", industry="industry", is_trust=True
        )

    def test_get_current_vals(self):
        # url
        url = reverse("web:api_get_current_vals")
        self.assertEqual(url, "/nams/api/get_current_vals/")
        # GET
        response = self.client.get(url)
        data = json.loads(response.body)
        codes = set(d['code'] for d in data)
        vals = {d['code']: d['val'] for d in data}
        # 存在の確認
        self.assertTrue(self.stock1.code in codes)
        self.assertTrue(self.stock2.code in codes)
        self.assertTrue(self.stock3.code in codes)
        # 値の確認
        self.assertEqual(self.stock1.current_val(), vals[self.stock1.code])
        self.assertEqual(self.stock2.current_val(), vals[self.stock2.code])
        self.assertEqual(self.stock3.current_val(), vals[self.stock3.code])

    def test_create_order(self):
        # url
        url = reverse("web:api_create_order")
        self.assertEqual(url, "/nams/api/create_order/")



