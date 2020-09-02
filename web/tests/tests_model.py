from django.test import TestCase
from web.models import Stock, Order, Entry, AssetStatus, ReasonWinLoss
from web.models import StockValueData, StockFinancialData, SBIAlert, AssetTarget
from django.contrib.auth.models import User
from datetime import datetime, date
# Create your tests here.


class ModelTest(TestCase):
    now = datetime.now()
    today = date.today()

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.s = Stock.objects.create(
            code=1570,
            name="test{}".format(1),
            market="market{}".format(1),
            industry="industry{}".format(1),
            is_trust=False
        )
        self.t = Stock.objects.create(
            code="64317081",
            name="test{}".format(1),
            market="market{}".format(1),
            industry="industry{}".format(1),
            is_trust=True
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
        self.bto = Order.objects.create(
            user=self.u,
            stock=self.t,
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
        self.sto = Order.objects.create(
            user=self.u,
            stock=self.t,
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
        self.assertEqual(c, 2)

    def test_order(self):
        c = Order.objects.count()
        self.assertEqual(c, 4)

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
        # 利確株価/損切株価での利益
        self.assertEqual(e.profit_profit_determination(), (e.border_profit_determination-e.val_buy())*e.num_buy())
        self.assertEqual(e.profit_loss_cut(), (e.border_loss_cut-e.val_buy()) * e.num_buy())

    def test_assetstaus(self):
        astatus = AssetStatus.objects.create(
            buying_power=1000000,
            nisa_power=1000000,
            sum_stock=0,
            sum_trust=0,
            sum_other=0,
            date=date.today(),
            investment=1000000,
            user=self.u,
        )
        self.assertEqual(AssetStatus.objects.count(), 1)
        # 準備
        entry = Entry.objects.create(
            user=self.u,
            stock=self.s,
            memo="test_entry",
            border_loss_cut=1000,
            border_profit_determination=1200,
        )
        entry_t = Entry.objects.create(
            user=self.u,
            stock=self.t,
            memo="test_entry",
            border_loss_cut=1000,
            border_profit_determination=1200,
        )
        self.bo.entry = entry
        self.bo.save()
        self.bto.entry = entry_t
        self.bto.save()
        # update：エントリーを参照して、各種値を更新
        astatus.update_status()
        self.assertEqual(astatus.sum_stock, self.bo.num * self.bo.stock.current_val())
        self.assertEqual(astatus.sum_trust, self.bto.num * self.bto.stock.current_val())

    def test_stockvaludedata(self):
        StockValueData.objects.create(
            stock=self.s, date=self.today,
            val_high=1200, val_low=1100, val_open=1150, val_close=1170,
            turnover=50000
        )
        self.assertEqual(StockValueData.objects.count(), 1)

    def test_stockfinancialdata(self):
        StockFinancialData.objects.create(
            stock=self.s, date=self.today,
            interest_bearing_debt=100.0,
            roa=10.0, roe=10.0, sales=10.0, assets=10.0,
            eps=10.0, net_income=10.0, bps=10.0, roa_2=10.0,
            operating_income=10.0, equity_ratio=10.0,
            capital=10.0, recurring_profit=10.0,
            equity=10.0, pbr_f=10.0, eps_f=10.0,
            market_value=10.0, per_f=10.0, dividend_yield=10.0, bps_f=10.0,
        )
        self.assertEqual(StockFinancialData.objects.count(), 1)

    def test_reasonwinloss(self):
        self.assertEqual(ReasonWinLoss.objects.count(), 2)

    def test_sbialert(self):
        self.assertEqual(SBIAlert.objects.count(), 0)
        sbialert = SBIAlert.objects.create(
            stock=self.s, val=1, type=2,
        )
        self.assertEqual(SBIAlert.objects.count(), 1)
        self.assertEqual(sbialert.type, 2)
        self.assertEqual(sbialert.stock, self.s)
        self.assertEqual(sbialert.val, 1)
        self.assertEqual(sbialert.created_at.date(), date.today())
        self.assertIsNone(sbialert.checked_at)
        self.assertTrue(sbialert.is_active)

    def test_assettarget(self):
        d = date(2020, 1, 1)
        self.assertEqual(AssetTarget.objects.count(), 0)
        atarget = AssetTarget.objects.create(
            date=d,  val_investment=3000000, val_target=3300000, memo="memo"
        )
        self.assertEqual(AssetTarget.objects.count(), 1)
        astatus = AssetStatus.objects.create(
            buying_power=1000000,
            nisa_power=1000000,
            sum_stock=3400000,
            sum_trust=0,
            sum_other=0,
            date=d,
            investment=3100000,
            user=self.u,
        )
        self.assertTrue(atarget.is_achieved_target())
        self.assertTrue(atarget.is_achieved_investment())
        self.assertEqual(atarget.diff_target(), astatus.get_total()-atarget.val_target)
        self.assertEqual(atarget.diff_investment(), astatus.investment - atarget.val_investment)
        self.assertEqual(atarget.actual_target(), astatus.get_total())
        self.assertEqual(atarget.actual_investment(), astatus.investment)
        self.assertEqual(atarget.actual_date(), astatus.date)