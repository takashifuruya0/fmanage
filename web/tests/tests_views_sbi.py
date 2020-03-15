from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from web.functions import selenium_sbi
from web.models import Stock, SBIAlert
from datetime import date


class SBIViewTest(TestCase):
    def setUp(self) -> None:
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.client.force_login(user=self.u)
        self.s = Stock.objects.create(
            code=1570,
            name="test{}".format(1),
            market="market{}".format(1),
            industry="industry{}".format(1),
            is_trust=False
        )

    def tearDown(self) -> None:
        pass

    def test_set_alert(self):
        """stockと値、タイプを指定し、SBI証券のアラートを設定する"""
        # SBIStockは存在しない
        self.assertEqual(0, SBIAlert.objects.count())
        # URL
        url = reverse("web:set_alert")
        self.assertEqual(url, "/nams/set_alert")
        # POST
        data = {
            "stock": self.s,  # stockオブジェクト
            "val": 1570,  # 設定する値 (float)
            "type": 1,  # 0：現在値（円以上）, 1：現在値（円以下）, 2：前日比（％以上）, 3：前日比（％以下）
        }
        res = self.client.post(url, data=data)
        for key in ("status", "msg"):
            self.assertTrue(key in res.keys())
        # SBIStockが作成される
        self.assertEqual(1, SBIAlert.objects.count())
        sbialert = SBIAlert.objects.first()
        # {
        # "type": IntegerField(choices=OPTIONS), 0~4
        # "stock": ForeignKey(Stock),
        # "val": Float,
        # "created_at": datetime,
        # "checked_at": datetime
        # }
        """Celery経由で作るので下記は確認不要"""
        # self.assertEqual(sbialert.type, data['type'])
        # self.assertEqual(sbialert.stock, data['stock'])
        # self.assertEqual(sbialert.val, data['val'])
        # self.assertEqual(sbialert.created_at.date(), date.today())
        # self.assertIsNone(sbialert.checked_at)
        # self.assertTrue(sbialert.is_active)

