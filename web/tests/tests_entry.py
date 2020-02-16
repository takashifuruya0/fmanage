from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from datetime import datetime
# Create your tests here.
from django.urls import reverse


class ModelTest(TestCase):
    num_stock = 3

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')

        for i in range(self.num_stock):
            self.s = Stock.objects.create(
                code=1000+i,
                name="test{}".format(i),
                market="market{}".format(i),
                industry="industry{}".format(i),
                is_trust=True if i == 0 else False
            )
        Order.objects.create(
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

    def test_entry_create(self):
        # Entryの作成
        url = reverse('web:entry_create')
        self.client.force_login(self.u)
        data = {
            "user": self.u,
            "stock": self.s,
            "border_profit_determination": 1000,
            'border_loss_cut': 900,
            'reason_win_loss': None,
            'memo': "Test",
            "is_plan": True,
        }
        self.client.post(url, data)
        e = Entry.objects.last()
        e_dict = e.__dict__
        for k in data.keys():
            self.assertEqual(e_dict[k], data[k])