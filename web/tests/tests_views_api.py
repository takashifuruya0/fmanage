from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
from web.models import AssetStatus, Stock, SBIAlert, Entry, Order
from web.functions import mylib_asset
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
        self.astatus = AssetStatus.objects.create(
            date=date.today(),
            user=self.u,
            buying_power=2000000,
            investment=1000000,
            nisa_power=1000000,
            sum_stock=0,
            sum_trust=0,
            sum_other=0,
        )

    def test_get_current_vals(self):
        """
        現在株価一覧取得
        """
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

    def test_create_order_remaining(self):
        """
        GASからデータが来て、order_processが動き、EntryをCloseさせない
        """
        # url
        url = reverse("web:api_create_order")
        self.assertEqual(url, "/nams/api/create_order/")
        # POST
        postdata = {
            "1570_現物買": {
                "datetime": "2020-03-11 09:00",
                "code": 1570,
                "is_buy": True,
                "num": 100,
                "val": 15000
            },
            "1570_現物売": {
                "datetime": "2020-03-11 09:14",
                "code": 1570,
                "is_buy": False,
                "num": 50,
                "val": 16000
            }
        }
        response = self.client.post(url, data=json.dumps(postdata), content_type="application/json")
        data = json.loads(response.content)
        # check:　Responseが正しい
        for key in ("status", "message", "data"):
            self.assertTrue(key in data.keys())
        self.assertTrue(data["status"])
        # check: Astatusが一つのまま
        self.assertEqual(AssetStatus.objects.count(), 1)
        astatus = AssetStatus.objects.last()
        # check: Orderが2つできている
        self.assertEqual(Order.objects.count(), 2)
        bo = Order.objects.get(is_buy=True)
        so = Order.objects.get(is_buy=False)
        # check: Entryが一つできている
        self.assertEqual(Entry.objects.count(), 1)
        e = Entry.objects.first()
        self.assertEqual(bo.entry, e)
        self.assertEqual(so.entry, e)
        # check: 保有株資産額が正しく計算されている
        self.assertEqual(astatus.sum_stock, int((bo.num - so.num)*bo.stock.current_val()))
        # check: 買付余力が正しく計算されている
        bpa = 2000000 - bo.num * bo.val - bo.commission + so.val * so.num - so.commission - (so.val-bo.val) * 0.2 * so.num
        self.assertEqual(astatus.buying_power, int(bpa))

    def test_create_order_close(self):
        """
        GASからデータが来て、order_processが動き、EntryをCloseさせる
        """
        # 事前準備
        buying_power = AssetStatus.objects.first().buying_power
        data = {
          "1571_現物売": {
            "datetime": "2018-03-06 14:14",
            "code": 1571,
            "is_buy": False,
            "num": 220,
            "val": 1738
          },
          "1571_現物買": {
            "datetime": "2018-03-06 14:12",
            "code": 1571,
            "is_buy": True,
            "num": 220,
            "val": 1740
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
        stock = Stock.objects.get(code=1571)
        buy_order = Order.objects.get(stock=stock, is_buy=True)
        sell_order = Order.objects.get(stock=stock, is_buy=False)
        # Entryが作成され、buy_order, sell_orderが紐付いている
        entry = Entry.objects.get(stock=stock)
        self.assertEqual(entry, buy_order.entry)
        self.assertEqual(entry, sell_order.entry)
        self.assertTrue(entry.is_closed)
        self.assertFalse(entry.is_plan)
        # AssetStatusが更新される
        astatus_after = AssetStatus.objects.first()
        buying_power_after = astatus_after.buying_power
        sum_stock_after = astatus_after.sum_stock
        val_order = data['1571_現物買']['num'] * data['1571_現物買']['val'] - data['1571_現物売']['num'] * data['1571_現物売']['val']
        commission = buy_order.commission + sell_order.commission
        self.assertEqual(sum_stock_after, 0)
        self.assertEqual(buying_power_after, buying_power - val_order - commission)

    def test_receive_alert(self):
        """
        GASからデータが来て、AlertをSlack通知し、SBIAlertをis_active=Falseとする
        :return:
        """
        # url
        url = reverse("web:api_receive_alert")
        self.assertEqual(url, "/nams/api/receive_alert/")
        # 事前確認
        self.assertTrue(1, SBIAlert.objects.filter(stock=self.stock1, type=2).count())
        # POST
        postdata = {
          "message": "2020/03/03 13:22に\r\nアラート条件\r\n前日比1\r\n％以上\r\nに達しました。\r\n日経ダブルインバ\r\n1357 東証\r\n現在値:1,063\r\n現時刻:2020/03/03 13:22\r\n前日比:+11\r\n出来高:61,214,318\r\n始値  :1,022\r\n高値  :1,063\r\n安値  :1,015\r\n売気配:1,063\r\n買気配:1,061\r\n買残  :72,668,214\r\n前週比:-2,111,136\r\n売残  :2,301,459\r\n前週比:-494,396\r\n倍率 :+31.57",
          "code": "1570",
          "val": 1,
          "type": 2
        }
        response = self.client.post(url, data=json.dumps(postdata), content_type="application/json")
        data = json.loads(response.content)
        for key in ("status", "message"):
            self.assertTrue(key in data.keys())
        self.assertTrue(data["status"])
        # SBIAlertの確認
        sbialert = SBIAlert.objects.filter(stock=self.stock1, type=2).first()
        self.assertFalse(sbialert.is_active)
        self.assertEqual(sbialert.checked_at.date(), date.today())
        self.assertEqual(sbialert.message, postdata["message"])

    # def test_slack_interactive(self):
    #     # url
    #     url = reverse("web:api_slack_interactive")
    #     self.assertEqual(url, "/nams/api/slack_interactive/")
    #     # post
    #     payload = {
    #         "type": "interactive_message",
    #         "actions": [
    #             {
    #                 "name": "current_price",
    #                 "type": "button",
    #                 "value": "1813"
    #             }
    #         ],
    #         "callback_id": "callback_id value",
    #         "team": {"id": "", "domain": ""},
    #         "channel": {"id": "", "name": ""},
    #         "user": {"id": "", "name": ""},
    #         "action_ts": "1584868490.062878",
    #         "message_ts": "1584865218.006500",
    #         "attachment_id": "1",
    #         "token": "",
    #         "is_app_unfurl": False,
    #         "original_message": {},
    #         "response_url": "",
    #         "trigger_id": "trigger_id",
    #     }
    #     postdata = {"payload": str(payload)}
    #     response = self.client.post(url, data=json.dumps(postdata), content_type="application/json")
    #     # current_priceでは、現在の値を入れて返す
    #     data = json.loads(response.content)
    #     self.assertTrue(data["replace_original"])
    #     self.assertEqual(data["response_type"], "in_channel")




