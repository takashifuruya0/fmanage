from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from datetime import datetime
# Create your tests here.


class ModelTest(TestCase):
    num_stock = 3

    def setUp(self):
        u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')

        for i in range(self.num_stock):
            s = Stock.objects.create(
                code=1000+i,
                name="test{}".format(i),
                market="market{}".format(i),
                industry="industry{}".format(i),
                is_trust=True if i == 0 else False
            )
        Order.objects.create(
            user=u,
            stock=s,
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

    def test_stock(self):
        c = Stock.objects.all().count()
        self.assertEqual(c, self.num_stock)

    def test_order(self):
        c = Order.objects.count()
        self.assertEqual(c, 1)

