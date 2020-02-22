from django.test import TestCase
from web.models import *
from django.contrib.auth.models import User
from web.functions import data_migration
from datetime import datetime
# Create your tests here.


class BatchTest(TestCase):

    def setUp(self):
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')

    def test_astatus(self):
        # 最初はAssetStatusは存在しない
        self.assertFalse(AssetStatus.objects.exists())
        # data_migration.astatus()を実行すると増える
        data_migration.astatus()
        astatus = AssetStatus.objects.all()
        self.assertTrue(astatus.exists())
        num_1 = astatus.count()
        # 最新の日付データを削除し、数を確認
        alast = astatus.order_by('-date').first()
        alast_date = alast.date
        alast.delete()
        num_2 = AssetStatus.objects.count()
        self.assertEqual(num_1, num_2+1)
        self.assertNotEqual(AssetStatus.objects.order_by('-date').first().date, alast_date)
        # 再びdata_migration.astatus()を実行すると、削除した分だけ数が増える
        data_migration.astatus()
        num_3 = AssetStatus.objects.count()
        self.assertEqual(num_1, num_3)
        self.assertEqual(AssetStatus.objects.order_by('-date').first().date, alast_date)
