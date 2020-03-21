from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from web.models import AssetStatus, Stock, SBIAlert
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
        self.sbialert = SBIAlert.objects.create(
            stock=self.stock1, type=2, val=1
        )

    def test_get_current_vals(self):
        # url
        url = reverse("web:api_get_current_vals")
        self.assertEqual(url, "/nams/api/get_current_vals/")
        # GET
        response = self.client.get(url)
        data = json.loads(response.content)
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

    def test_receive_alert(self):
        # url
        url = reverse("web:api_receive_alert")
        self.assertEqual(url, "/nams/api/receive_alert/")
        # 事前確認
        self.assertTrue(1, SBIAlert.objects.filter(stock=self.stock1, type=2).count())
        # POST
        postdata = {
          "message": "2020/03/03 13:22に\r\nアラート条件\r\n前日比1\r\n％以上\r\nに達しました。\r\n日経ダブルインバ\r\n1357 東証\r\n現在値:1,063\r\n現時刻:2020/03/03 13:22\r\n前日比:+11\r\n出来高:61,214,318\r\n始値  :1,022\r\n高値  :1,063\r\n安値  :1,015\r\n売気配:1,063\r\n買気配:1,061\r\n買残  :72,668,214\r\n前週比:-2,111,136\r\n売残  :2,301,459\r\n前週比:-494,396\r\n倍率 :+31.57\r\n\r\n-- \r\n古屋敬士\r\nTel  08054506740\r\nMail takashi.furuya.0@gmail.com\r\n",
          "code": "1570",
          "val": 1,
          "type": 2
        }
        response = self.client.post(url, data=json.dumps(postdata), content_type="application/json")
        data = json.loads(response.content)
        for key in ("status", "message"):
            self.assertTrue(key in data.keys())
        # SBIAlertの確認
        sbialert = SBIAlert.objects.filter(stock=self.stock1, type=2).first()
        self.assertFalse(sbialert.is_active)
        self.assertEqual(sbialert.checked_at.date(), date.today())
        self.assertEqual(sbialert.message, postdata["message"])



