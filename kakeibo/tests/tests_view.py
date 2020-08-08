from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from kakeibo.models import Kakeibos, Usages, Resources, SharedKakeibos, Credits, CreditItems, Budget
from kakeibo.models import Event
from asset.models import AssetStatus
from datetime import date
import logging
logger = logging.getLogger('django')
from django.conf import settings

# Create your tests here.


class ViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="user1", password="password1")
        self.client.force_login(user=user)
        self.today = date.today()
        today = self.today
        usage = Usages.objects.create(name="usage", date=today, is_expense=True)
        usage_other = Usages.objects.create(name="その他", date=today, is_expense=True)
        resource = Resources.objects.create(name="resource", date=today, initial_val=10000)
        kakeibo = Kakeibos.objects.create(fee=100, usage=usage, way="支出（現金）", date=today, move_from=resource)
        shared = SharedKakeibos.objects.create(fee=100, usage=usage, paid_by="敬士", date=today, is_settled=False)
        event = Event.objects.create(name="テストイベント", memo="テストメモ", sum_plan=10000, is_active=True, date=today)
        citem = CreditItems.objects.create(
            name="citem",
            usage=usage,
            date=self.today
        )
        credit = Credits.objects.create(
            fee=100,
            date=self.today,
            debit_date=self.today,
            credit_item=citem
        )
        astatus = AssetStatus.objects.create(
            total=100000,
            date=self.today,
            buying_power=50000,
            stocks_value=30000,
            other_value=20000,
            investment=100000
        )
        budget = Budget.objects.create(
            date=date(1999, 1, 1), takashi=90000, hoko=60000
        )

    def test_dashboard(self):
        url = reverse("kakeibo:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('kakeibo/dashboard.html')

    def test_mine(self):
        url = reverse("kakeibo:mine")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('kakeibo/mine.html')

    def test_shared(self):
        url = reverse("kakeibo:shared")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url = reverse("kakeibo:shared")
        response = self.client.get(url+"?yearmonth={}-{}".format(self.today.year, str(self.today.month).zfill(2)))
        self.assertEqual(response.status_code, 200)

    def test_credit(self):
        url = reverse("kakeibo:credit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_kakeibo_list(self):
        url = reverse("kakeibo:kakeibo_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_kakeibo_detail(self):
        pk = Kakeibos.objects.last().pk
        url = reverse("kakeibo:kakeibo_detail", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_shared_list(self):
        url = reverse("kakeibo:shared_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_shared_detail(self):
        pk = SharedKakeibos.objects.last().pk
        url = reverse("kakeibo:shared_detail", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_credit_list(self):
        url = reverse("kakeibo:credit_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_credit_detail(self):
        pk = Credits.objects.last().pk
        url = reverse("kakeibo:credit_detail", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_credit_item_list(self):
        url = reverse("kakeibo:credit_item_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_credit_item_detail(self):
        pk = CreditItems.objects.last().pk
        url = reverse("kakeibo:credit_item_detail", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_usage_list(self):
        url = reverse("kakeibo:usage_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_usage_detail(self):
        pk = Usages.objects.last().pk
        url = reverse("kakeibo:usage_detail", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_list(self):
        url = reverse("kakeibo:event_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_event_detail(self):
        pk = Event.objects.last().pk
        url = reverse("kakeibo:event_detail", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_kakeibo(self):
        pk = Kakeibos.objects.last().pk
        url = reverse("kakeibo:kakeibo_update", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_kakeibo_save(self):
        kdict = Kakeibos.objects.first().__dict__
        url = reverse("kakeibo:kakeibo_update", kwargs={"pk": kdict['id']})
        response = self.client.post(url, {
            "date": date(2019, 1, 1),
            "fee": kdict['fee'] + 200,
            "way": kdict['way'],
            "usage": kdict['usage_id'],
        })
        kakeibo_updated = Kakeibos.objects.get(pk=kdict['id'])
        # redirect
        self.assertRedirects(response, reverse("kakeibo:kakeibo_detail", kwargs={"pk": kdict['id']}))
        # 修正した要素
        self.assertNotEqual(kakeibo_updated.fee, kdict['fee'])
        self.assertNotEqual(kakeibo_updated.date, kdict['date'])
        # 修正していない要素
        self.assertEqual(kakeibo_updated.way, kdict['way'])
        self.assertEqual(kakeibo_updated.usage.pk, kdict['usage_id'])

    def test_update_shared_save(self):
        kdict = SharedKakeibos.objects.last().__dict__
        url = reverse("kakeibo:shared_update", kwargs={"pk": kdict['id']})
        response = self.client.post(url, {
            "date": date(2019, 1, 1),
            "fee": kdict['fee'] + 200,
            "paid_by": "朋子",
            "usage": kdict['usage_id'],
        })
        shared_updated = SharedKakeibos.objects.get(pk=kdict['id'])
        # redirect
        self.assertRedirects(response, reverse("kakeibo:shared_detail", kwargs={"pk": kdict['id']}))
        # 修正した要素
        self.assertNotEqual(shared_updated.fee, kdict['fee'])
        self.assertNotEqual(shared_updated.date, kdict['date'])
        self.assertNotEqual(shared_updated.way, kdict['paid_by'])
        # 修正していない要素
        self.assertEqual(shared_updated.usage.pk, kdict['usage_id'])

    def test_update_credit_save(self):
        kdict = Credits.objects.last().__dict__
        url = reverse("kakeibo:credit_update", kwargs={"pk": kdict['id']})
        response = self.client.post(url, {
            "date": date(2019, 1, 1),
            "debit_date": kdict['date'],
            "fee": kdict['fee'] + 200,
            "credit_item": kdict["credit_item_id"],
        })
        credit_updated = Credits.objects.get(pk=kdict['id'])
        # redirect
        self.assertRedirects(response, reverse("kakeibo:credit_detail", kwargs={"pk": kdict['id']}))
        # 修正した要素
        self.assertNotEqual(credit_updated.fee, kdict['fee'])
        self.assertNotEqual(credit_updated.date, kdict['date'])
        # 修正していない要素
        self.assertEqual(credit_updated.credit_item.pk, kdict['credit_item_id'])
        self.assertEqual(credit_updated.debit_date, kdict['debit_date'])

    def test_update_credit_item_save(self):
        kdict = CreditItems.objects.last().__dict__
        url = reverse("kakeibo:credit_item_update", kwargs={"pk": kdict['id']})
        response = self.client.post(url, {
            "name": kdict["name"] + "_rev",
            "usage": kdict['usage_id']
        })
        credit_item_updated = CreditItems.objects.get(pk=kdict['id'])
        # redirect
        self.assertRedirects(response, reverse("kakeibo:credit_item_detail", kwargs={"pk": kdict['id']}))
        # 修正した要素
        self.assertNotEqual(credit_item_updated.name, kdict['name'])
        # 修正していない要素
        self.assertEqual(credit_item_updated.usage.pk, kdict['usage_id'])

    def test_update_event_save(self):
        kdict = Event.objects.last().__dict__
        url = reverse("kakeibo:event_update", kwargs={"pk": kdict['id']})
        response = self.client.post(url, {
            "date": date(2019, 1, 1),
            "name": kdict['name'],
            "memo": kdict['memo'],
            "detail": "OK",
            "sum_plan": kdict['sum_plan'],
            "is_active": True,
        })
        event_updated = Event.objects.get(pk=kdict['id'])
        # redirect
        self.assertRedirects(response, reverse("kakeibo:event_detail", kwargs={"pk": kdict['id']}))
        # 修正した要素
        self.assertEqual(event_updated.detail, "OK")
        # 修正していない要素
        self.assertEqual(event_updated.memo, kdict['memo'])

    def test_create_event(self):
        url = reverse("kakeibo:event_create")
        response = self.client.post(url, {
            "date": date(2019, 1, 1),
            "name": "t",
            "memo": "t",
            "detail": "t",
            "sum_plan": 10000,
            "is_active": True,
        })
        event_created = Event.objects.last()
        # redirect
        self.assertRedirects(response, reverse("kakeibo:event_detail", kwargs={"pk": event_created.pk}))
