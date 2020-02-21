from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
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
        self.so = Order.objects.create(
            user=self.u,
            stock=self.s,
            datetime=self.now,
            is_nisa=False,
            is_buy=False,
            is_simulated=False,
            num=100,
            val=1200,
            commission=250,
            entry=None,
            chart=None,
        )
        self.wr = ReasonWinLoss.objects.create(
            reason="Won",
            is_win=True,
            description="WOn"
        )
        self.lr = ReasonWinLoss.objects.create(
            reason="Lost",
            is_win=False,
            description="Lost"
        )

    def test_stock(self):
        c = Stock.objects.all().count()
        self.assertEqual(c, 1)

    def test_order(self):
        c = Order.objects.count()
        self.assertEqual(c, 2)

    def test_entry(self):
        e = Entry.objects.create(
            user=self.u,
            stock=self.s,
            memo="test_entry",
            border_loss_cut=1000,
            border_profit_determination=1200,
        )
        # 注文が紐付いていないと、is_plan=True、is_closed=False
        self.assertTrue(e.is_plan)
        self.assertFalse(e.is_closed)
        # 残数＜０となるとエラー
        try:
            self.so.entry = e
            self.so.save()
            self.fail('Error: entry.remaining() < 0')
        except Exception:
            pass
        # 注文が紐付いたら、is_plan=False, is_closed=False
        self.bo.entry = e
        self.bo.save()
        self.assertFalse(e.is_closed)
        self.assertFalse(e.is_plan)
        self.assertEqual(e.remaining(), self.bo.num)
        # 売り注文も紐付いて、remaining=0ならば、is_plan=False, is_closed=True
        self.so.entry = e
        self.so.save()
        self.assertTrue(e.is_closed)
        self.assertFalse(e.is_plan)
        self.assertEqual(e.remaining(), 0)

