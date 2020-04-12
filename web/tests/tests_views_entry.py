from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from datetime import datetime
# Create your tests here.
from django.urls import reverse


class ModelTest(TestCase):

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.client.force_login(user=self.u)
        self.s = Stock.objects.create(
            code=8410,
            name="test",
            market="market",
            industry="industry",
            is_trust=False
        )
        self.o = Order.objects.create(
            user=self.u,
            stock=self.s,
            datetime=datetime.now(),
            is_nisa=False,
            is_buy=True,
            is_simulated=False,
            num=100,
            val=1000,
            commission=250,
            entry=None,
            chart=None,
        )
        self.r = ReasonWinLoss.objects.create(reason="OK", is_win=True)
        self.e = Entry.objects.create(user=self.u, stock=self.s, is_plan=True, memo="TEST")

    def test_entry_detail(self):
        response = self.client.get(reverse('web:entry_detail', kwargs={"pk": self.e.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('web/entry_detail.html')

    def test_entry_list(self):
        response = self.client.get(reverse('web:entry_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('web/entry_list.html')

    def test_entry_update(self):
        url = reverse("web:entry_edit", kwargs={"pk": self.e.pk})
        self.client.get(url)
        self.assertTemplateUsed("web/entry_edit.html")
        data = {
            "user": self.u.pk,
            "stock": self.s.pk,
            "border_profit_determination": 1000,
            'border_loss_cut': 900,
            'reason_win_loss': self.r.pk,
            'memo': "A",
            "is_plan": True,
            "num_plan": 0,
            "entry_type": "中期",
        }
        response = self.client.post(url, data=data)
        self.e = Entry.objects.get(pk=self.e.pk)
        self.assertRedirects(response, reverse("web:entry_detail", kwargs={"pk": self.e.pk}))
        self.assertEqual(self.e.user.pk, data["user"])
        self.assertEqual(self.e.stock.pk, data["stock"])
        self.assertEqual(self.e.border_profit_determination, data["border_profit_determination"])
        self.assertEqual(self.e.border_loss_cut, data["border_loss_cut"])
        self.assertEqual(self.e.memo, data["memo"])
        self.assertEqual(self.e.is_plan, data["is_plan"])

    def test_entry_create(self):
        # Entryの作成
        url = reverse('web:entry_create')
        data = {
            "user": self.u.pk,
            "stock": self.s.pk,
            "border_profit_determination": 1000,
            'border_loss_cut': 900,
            'reason_win_loss': self.r.pk,
            'memo': "A",
            "is_plan": True,
            "num_plan": 0,
            "entry_type": "中期",
        }
        response = self.client.post(url, data=data)
        self.e = Entry.objects.last()
        self.assertRedirects(response, reverse("web:entry_detail", kwargs={"pk": self.e.pk}))
        self.assertEqual(self.e.user.pk, data["user"])
        self.assertEqual(self.e.stock.pk, data["stock"])
        self.assertEqual(self.e.border_profit_determination, data["border_profit_determination"])
        self.assertEqual(self.e.border_loss_cut, data["border_loss_cut"])
        self.assertEqual(self.e.memo, data["memo"])
        self.assertEqual(self.e.is_plan, data["is_plan"])

    def test_entry_delete(self):
        url = reverse("web:entry_delete", kwargs={"pk": self.e.pk})
        response = self.client.delete(url)
        self.assertRedirects(response, reverse("web:entry_list"))
        self.assertFalse(Entry.objects.filter(pk=self.e.pk).exists())
