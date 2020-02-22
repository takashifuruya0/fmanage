from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from web.functions import asset_lib
from datetime import datetime
# Create your tests here.


class ModelTest(TestCase):
    now = datetime.now()

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.s = Stock.objects.create(
            code=1000,
            name="test{}".format(1),
            market="market{}".format(1),
            industry="industry{}".format(1),
            is_trust=False
        )
        self.bo = Order.objects.create(
            user=self.u,
            stock=self.s,
            datetime=self.now,
            is_nisa=False,
            is_buy=True,
            is_simulated=False,
            num=100,
            val=1000,
            commission=250,
            entry=None,
            chart=None,
        )
        self.astatus = AssetStatus.objects.create(
            date=date.today(),
            user=self.u,
            buying_power=1000000,
            investment=1000000,
            nisa_power=1000000,
            sum_stock=0,
            sum_trust=0,
            sum_other=0,
        )

    def test_linking_order_to_plan_entry(self):
        """売り注文作成時に、同じStockのEntry(is_plan=True)があれば紐付け＆is_plan=False"""
        e = Entry.objects.create(stock=self.s, user=self.u, is_plan=True)
        self.assertEqual(Entry.objects.count(), 1)
        result = asset_lib.order_process(order=self.bo, user=self.u)
        self.assertTrue(result['status'])
        # 既存Entry(is_plan=True)に紐付け
        self.assertEqual(self.bo.entry, e)
        # is_plan=False and is_closed=False and stock=self.s and user=self.u
        self.assertFalse(self.bo.entry.is_plan)
        self.assertFalse(self.bo.entry.is_closed)
        self.assertEqual(self.bo.entry.stock, self.s)
        self.assertEqual(self.bo.entry.user, self.u)
        # Astatusが更新される
        self.astatus = AssetStatus.objects.first()
        self.assertEqual(self.astatus.buying_power, 1000000 - self.bo.num * self.bo.val - self.bo.commission)
        self.assertEqual(self.astatus.sum_stock, self.bo.num * self.bo.val)

    def test_linking_order_to_new_entry(self):
        """売り注文作成時に、同じStockのEntryがなければ新規作成して紐付け"""
        result = asset_lib.order_process(order=self.bo, user=self.u)
        self.assertTrue(result['status'])
        self.assertEqual(Entry.objects.count(), 1)
        # is_plan=False and is_closed=False and stock=self.s and user=self.u
        self.assertFalse(self.bo.entry.is_plan)
        self.assertFalse(self.bo.entry.is_closed)
        self.assertEqual(self.bo.entry.stock, self.s)
        self.assertEqual(self.bo.entry.user, self.u)
        # Astatusが更新される
        self.astatus = AssetStatus.objects.first()
        self.assertEqual(self.astatus.buying_power, 1000000 - self.bo.num * self.bo.val - self.bo.commission)
        self.assertEqual(self.astatus.sum_stock, self.bo.num * self.bo.val)

    def test_over_buying_power(self):
        """売り注文が買付余力を超えているとエラー"""
        bp = self.bo.num * self.bo.val - 1
        self.astatus.buying_power = bp
        self.astatus.save()
        # 買付余力もsum_stockも変更なし
        result = asset_lib.order_process(order=self.bo, user=self.u)
        self.assertFalse(result['status'])
        self.astatus = AssetStatus.objects.first()
        self.assertEqual(self.astatus.buying_power, bp)
        self.assertEqual(self.astatus.sum_stock, 0)


