from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
import json
# Create your tests here.


class ViewsAjaxTest(TestCase):

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.astatus = AssetStatus.objects.create(
            date=(date.today()+relativedelta(days=-1)), user=self.u,
            buying_power=1000000, investment=1000000, nisa_power=1000000,
            sum_stock=0, sum_trust=0, sum_other=0,
        )
        self.s = Stock.objects.create(
            code=1570, name="test{}".format(1),
            market="market{}".format(1), industry="industry{}".format(1),
            is_trust=False
        )
        self.e = Entry.objects.create(user=self.u, stock=self.s, is_plan=True, memo="TEST")

    def test_activate_entry(self):
        """
        EntryをActivate
        """
        # EntryPlanが1件
        self.assertEqual(1, Entry.objects.filter(is_plan=True, is_closed=False).count())
        self.assertEqual(0, Entry.objects.filter(is_plan=True, is_closed=True).count())
        # URL
        url = reverse("web:ajax_activate_entry")
        self.assertEqual(url, "/nams/ajax/activate_entry/")
        # POST
        data = {
            "entry": self.e.pk,  # entryオブジェクト. formではPKが入る
        }
        res = self.client.post(url, data=data)
        res_data = json.loads(res.content)
        print(res_data)
        for key in ("status", "msg"):
            self.assertTrue(key in res_data.keys())
        # EntryInactivePlanが1件
        self.assertEqual(0, Entry.objects.filter(is_plan=True, is_closed=False).count())
        self.assertEqual(1, Entry.objects.filter(is_plan=True, is_closed=True).count())

    def test_deactivate_entry(self):
        """
        EntryをDeactivate
        """
        # EntryInactivePlanが1件
        self.e.is_closed = True
        self.e.save()
        self.assertEqual(0, Entry.objects.filter(is_plan=True, is_closed=False).count())
        self.assertEqual(1, Entry.objects.filter(is_plan=True, is_closed=True).count())
        # URL
        url = reverse("web:ajax_deactivate_entry")
        self.assertEqual(url, "/nams/ajax/deactivate_entry/")
        # POST
        data = {
            "entry": self.e.pk,  # entryオブジェクト. formではPKが入る
        }
        res = self.client.post(url, data=data)
        res_data = json.loads(res.content)
        print(res_data)
        for key in ("status", "msg"):
            self.assertTrue(key in res_data.keys())
        # EntryPlanが1件
        self.assertEqual(1, Entry.objects.filter(is_plan=True, is_closed=False).count())
        self.assertEqual(0, Entry.objects.filter(is_plan=True, is_closed=True).count())