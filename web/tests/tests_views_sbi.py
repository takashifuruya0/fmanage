# from django.test import TestCase
# from django.urls import reverse
# from django.contrib.auth.models import User
# from web.functions import mylib_selenium
# from web.models import Stock, SBIAlert, Entry
# from datetime import date
# import json
#
#
# class SBIViewTest(TestCase):
#     def setUp(self) -> None:
#         self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
#         self.client.force_login(user=self.u)
#         self.s = Stock.objects.create(
#             code=1570,
#             name="test{}".format(1),
#             market="market{}".format(1),
#             industry="industry{}".format(1),
#             is_trust=False
#         )
#
#     def tearDown(self) -> None:
#         pass
#
#     def test_set_alert(self):
#         """stockと値、タイプを指定し、SBI証券のアラートを設定する"""
#         # SBIAlertは存在しない
#         self.assertEqual(0, SBIAlert.objects.count())
#         # URL
#         url = reverse("web:ajax_set_alert")
#         self.assertEqual(url, "/nams/ajax/set_alert/")
#         # POST
#         data = {
#             "stock": self.s.pk,  # stockオブジェクト. formではPKが入る
#             "val": 1570,  # 設定する値 (float)
#             "type": 1,  # 0：現在値（円以上）, 1：現在値（円以下）, 2：前日比（％以上）, 3：前日比（％以下）
#         }
#         res = self.client.post(url, data=data)
#         res_data = json.loads(res.content)
#         print(res_data)
#         for key in ("status", "msg"):
#             self.assertTrue(key in res_data.keys())
#         # SBIStockが作成される
#         self.assertEqual(1, SBIAlert.objects.count())
#         # {
#         # "type": IntegerField(choices=OPTIONS), 0~4
#         # "stock": ForeignKey(Stock),
#         # "val": Float,
#         # "created_at": datetime,
#         # "checked_at": datetime
#         # }
#         """Celery経由で作るので下記は確認不要"""
#         # sbialert = SBIAlert.objects.first()
#         # self.assertEqual(sbialert.type, data['type'])
#         # self.assertEqual(sbialert.stock, data['stock'])
#         # self.assertEqual(sbialert.val, data['val'])
#         # self.assertEqual(sbialert.created_at.date(), date.today())
#         # self.assertIsNone(sbialert.checked_at)
#         # self.assertTrue(sbialert.is_active)
#
#     def test_buy_order(self):
#         """EntryPlanのnum_planの口数で、SBI証券で成行買い注文を実施"""
#         # prepare
#         e = Entry.objects.create(
#             user=self.u,
#             stock=self.s,
#             memo="test_entry",
#             border_loss_cut=1000,
#             border_profit_determination=1200,
#         )
#         # URL
#         url = reverse("web:ajax_buy_order")
#         self.assertEqual(url, "/nams/ajax/buy_order/")
#         # POST
#         data = {
#             "entry": e.pk,  # Entryオブジェクト. formではPKが入る
#         }
#         res = self.client.post(url, data=data)
#         res_data = json.loads(res.content)
#         print(res_data)
#         for key in ("status", "msg"):
#             self.assertTrue(key in res_data.keys())
#         # num_plan=Noneでは、status=False
#         self.assertFalse(res_data['status'])
#         # entry.is_in_order=False
#         e = Entry.objects.get(pk=e.pk)
#         self.assertFalse(e.is_in_order)
#         # num_plan=10に設定して、再度トライ
#         e.num_plan = 10
#         e.save()
#         # POST
#         data = {
#             "entry": e.pk,  # Entryオブジェクト. formではPKが入る
#         }
#         res = self.client.post(url, data=data)
#         res_data = json.loads(res.content)
#         print(res_data)
#         for key in ("status", "msg"):
#             self.assertTrue(key in res_data.keys())
#         # num_plan=Noneでは、status=False
#         self.assertTrue(res_data['status'])
#         # entry.is_in_order=True
#         e = Entry.objects.get(pk=e.pk)
#         self.assertTrue(e.is_in_order)

