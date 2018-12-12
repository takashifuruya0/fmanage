from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from kakeibo.models import Kakeibos, Usages, Resources, SharedKakeibos, Credits, CreditItems
from asset.models import AssetStatus
from datetime import date

# Create your tests here.


class ViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="user1", password="password1")
        self.client.force_login(user=user)
        today = date.today()
        usage = Usages.objects.create(name="usage", date=today, is_expense=True)
        resource = Resources.objects.create(name="resource", date=today, initial_val=10000)
        kakeibo = Kakeibos.objects.create(fee=100, usage=usage, way="支出（現金）", date=today, move_from=resource)
        shared = SharedKakeibos.objects.create(fee=100, usage=usage, paid_by="敬士", date=today, is_settled=False)
        citem = CreditItems.objects.create(
            name="citem",
            usage=usage,
            date=today
        )
        credit = Credits.objects.create(
            fee=100,
            date=today,
            debit_date=today,
            credit_item=citem
        )
        astatus = AssetStatus.objects.create(
            total=100000,
            date=today,
            buying_power=50000,
            stocks_value=30000,
            other_value=20000,
            investment=100000
        )

    def test_dashboard(self):
        url = reverse("kakeibo:dashboard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mine(self):
        url = reverse("kakeibo:mine")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_shared(self):
        url = reverse("kakeibo:shared")
        response = self.client.get(url)
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

    def test_update_kakeibo(self):
        pk = Kakeibos.objects.last().pk
        url = reverse("kakeibo:kakeibo_update", kwargs={"pk": pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_kakeibo_save(self):
        kdict = Kakeibos.objects.last().__dict__
        url = reverse("kakeibo:kakeibo_update", kwargs={"pk": kdict['id']})
        response = self.client.post(url, {
            "date": date(kdict['date'].year, kdict['date'].month, kdict['date'].day+1),
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