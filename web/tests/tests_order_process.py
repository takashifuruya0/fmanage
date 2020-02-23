from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from django.urls import reverse
from web.functions import asset_lib
from datetime import datetime
import json
import logging
logger = logging.getLogger('django')


class ModelTest(TestCase):
    now = datetime.now()
    now_so = datetime.now()

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.s = Stock.objects.create(
            code=1570,
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
        self.so = Order.objects.create(
            user=self.u,
            stock=self.s,
            datetime=self.now_so,
            is_nisa=False,
            is_buy=False,
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

    def test_linking_buy_order_to_plan_entry(self):
        """買い注文作成時に、同じStockのEntry(is_plan=True)があれば紐付け＆is_plan=False"""
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

    def test_linking_buy_order_to_new_entry(self):
        """買い注文作成時に、同じStockのEntryがなければ新規作成して紐付け"""
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

    def test_linking_sell_order_to_existing_entry(self):
        """売り注文作成時に、同じStockのEntryに紐付け。口数が違うのでCloseしない"""
        # 事前準備
        self.bo.num = self.bo.num + 10
        self.bo.save()
        asset_lib.order_process(order=self.bo, user=self.u)
        self.assertEqual(Entry.objects.count(), 1)
        self.assertEqual(self.bo.entry.num_linked_orders(), 1)
        # order_process
        result = asset_lib.order_process(order=self.so, user=self.u)
        self.assertTrue(result['status'])
        # is_plan=False and is_closed=True and stock=self.s and user=self.u
        entry_after = Entry.objects.get(stock=self.s, user=self.u)
        self.assertEqual(entry_after, self.so.entry)
        self.assertFalse(entry_after.is_plan)
        self.assertEqual(entry_after.remaining(), self.bo.num - self.so.num)
        self.assertFalse(entry_after.is_closed)
        self.assertEqual(entry_after.stock, self.s)
        self.assertEqual(entry_after.user, self.u)
        self.assertEqual(entry_after.num_linked_orders(), 2)
        # Astatusが更新される
        self.astatus = AssetStatus.objects.first()
        self.assertEqual(
            self.astatus.buying_power,
            1000000 - self.bo.num * self.bo.val - self.bo.commission + self.so.num * self.so.val - self.so.commission
        )
        self.assertEqual(self.astatus.sum_stock, (self.bo.num - self.so.num)*self.so.val)

    def test_linking_sell_order_to_existing_entry_and_close(self):
        """売り注文作成時に、同じStockのEntryに紐付け。口数が一緒なのでCloseもさせる"""
        # 事前準備
        self.bo.num = self.so.num
        self.bo.save()
        result = asset_lib.order_process(order=self.bo, user=self.u)
        self.assertTrue(result['status'])
        self.assertEqual(Entry.objects.count(), 1)
        # order_process
        result = asset_lib.order_process(order=self.so, user=self.u)
        self.assertTrue(result['status'])
        # is_plan=False and is_closed=True and stock=self.s and user=self.u
        entry_after = Entry.objects.get(stock=self.s, user=self.u)
        self.assertEqual(entry_after, self.so.entry)
        self.assertFalse(entry_after.is_plan)
        self.assertEqual(entry_after.remaining(), 0)
        self.assertTrue(entry_after.is_closed)
        self.assertEqual(entry_after.stock, self.s)
        self.assertEqual(entry_after.user, self.u)
        self.assertEqual(entry_after.num_linked_orders(), 2)
        # Astatusが更新される
        self.astatus = AssetStatus.objects.first()
        self.assertEqual(
            self.astatus.buying_power,
            1000000 - self.bo.num * self.bo.val - self.bo.commission + self.so.num * self.so.val - self.so.commission
        )
        self.assertEqual(self.astatus.sum_stock, 0)

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

    def test_api_order_process(self):
        """
        GASからデータが来て、order_processが動く
        """
        # 事前準備
        buying_power = AssetStatus.objects.first().buying_power
        data = {
          "1571_現物売": {
            "datetime": "2018-03-06 14:14",
            "order_id": "290\r",
            "code": 1571,
            "kind": "現物売",
            "num": 220,
            "price": 1738
          },
          "1571_現物買": {
            "datetime": "2018-03-06 14:12",
            "order_id": "290\r",
            "code": 1571,
            "kind": "現物買",
            "num": 220,
            "price": 1738
          }
        }
        json_data = json.dumps(data)
        # stock, orderがない
        self.assertFalse(Stock.objects.filter(code=1571).exists())
        self.assertFalse(Order.objects.filter(stock__code=1571).exists())
        # apiを叩く
        url = reverse("web:api_create_order")
        response = self.client.post(url, data=json_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        # StockとOrderが作成されている
        stock = Stock.objects.get(stock=1571)
        buy_order = Order.objects.get(stock=stock, is_buy=True)
        sell_order = Order.objects.get(stock=stock, is_buy=False)
        # Entryが作成され、buy_order, sell_orderが紐付いている
        entry = Entry.objects.get(stock=stock)
        self.assertEqual(entry, buy_order.entry)
        self.assertEqual(entry, sell_order.entry)
        self.assertTrue(entry.is_closed)
        self.assertFase(entry.is_plan)
        # AssetStatusが更新される
        astatus_after = AssetStatus.objects.first()
        buying_power_after = astatus_after.buying_power
        sum_stock_after = astatus_after.sum_stock
        val_order = data['1571_現物買']['num'] * data['1571_現物買']['val'] - data['1571_現物売']['num'] * data['1571_現物売']['val']
        commission = buy_order.commission + sell_order.commission
        self.assertEqual(sum_stock_after, val_order)
        self.assertEqual(buying_power_after, buying_power + val_order - commission)
