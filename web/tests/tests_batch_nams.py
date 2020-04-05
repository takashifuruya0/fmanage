from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from web.functions import mylib_asset
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from django.db.models import Count
# Create your tests here.


class BatchNamsTest(TestCase):

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

    def test_astatus(self):
        """
        前のAssetStatusをコピーして、今日の日付で作成する
        """
        # 最初は一つだけ
        self.assertEqual(AssetStatus.objects.count(), 1)
        # record_asset_status を実行すると
        res = mylib_asset.record_asset_status()
        # check: response
        for k in ("status", "asset_status", ):
            self.assertTrue(k in res)
        # check: 本日のAstatusが追加される
        self.assertEqual(AssetStatus.objects.count(), 2)
        # check: 昨日のレコードをコピー
        astatus_today = AssetStatus.objects.get(date=date.today())
        self.assertEqual(astatus_today.sum_stock, 0)
        self.assertEqual(astatus_today.sum_trust, 0)
        self.assertEqual(astatus_today.sum_other, 0)
        self.assertEqual(astatus_today.buying_power, 1000000)
        self.assertEqual(astatus_today.nisa_power, 1000000)
        self.assertEqual(astatus_today.investment, 1000000)
        # 株を買って、Entryができたとする
        bo = Order.objects.create(
            user=self.u, stock=self.s, datetime=datetime.now(),
            is_nisa=False, is_buy=True, is_simulated=False,
            num=100, val=1000, commission=250,
            entry=None, chart=None,
        )
        astatus_today.buying_power -= (bo.num * bo.val - bo.commission)
        astatus_today.save()
        # 再びrecord_asset_statusを実行
        res = mylib_asset.record_asset_status()
        astatus_today_updated = res['asset_status']
        self.assertEqual(AssetStatus.objects.count(), 2)
        self.assertEqual(astatus_today_updated.date, date.today())
        self.assertEqual(astatus_today_updated.sum_stock, bo.num*bo.stock.current_val())