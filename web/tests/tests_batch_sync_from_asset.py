# from django.test import TestCase
# from web.models import *
# from django.contrib.auth.models import User
# from web.functions import data_migration
# from django.db.models import Count
## Create your tests here.


# class BatchTest(TestCase):
#
#     def setUp(self):
#         self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
#
#     def test_astatus(self):
#         """最初はAssetStatusは存在しない"""
#         self.assertFalse(AssetStatus.objects.exists())
#         """data_migration.astatus()を実行すると増える"""
#         data_migration.astatus()
#         astatus = AssetStatus.objects.all()
#         self.assertTrue(astatus.exists())
#         num_1 = astatus.count()
#         """最新の日付データを削除し、数を確認"""
#         alast = astatus.order_by('-date').first()
#         alast_date = alast.date
#         alast.delete()
#         num_2 = AssetStatus.objects.count()
#         self.assertEqual(num_1, num_2+1)
#         self.assertNotEqual(AssetStatus.objects.order_by('-date').first().date, alast_date)
#         """再びdata_migration.astatus()を実行すると、削除した分だけ数が増える"""
#         data_migration.astatus()
#         num_3 = AssetStatus.objects.count()
#         self.assertEqual(num_1, num_3)
#         self.assertEqual(AssetStatus.objects.order_by('-date').first().date, alast_date)
#         """同じ日付は存在しない"""
#         unique_check = set(a['c'] for a in AssetStatus.objects.values('date').annotate(c=Count('pk')))
#         self.assertEqual(set([1, ]), unique_check)
#
#     def test_order(self):
#         # 最初はOrderが存在しない
#         self.assertFalse(Order.objects.exists())
#         # data_migration.orderを実行すると増える
#         data_migration.astatus()
#         data_migration.stock()
#         data_migration.order()
#         self.assertTrue(Order.objects.exists())
#         num_1 = Order.objects.count()
#         latest_order = Order.objects.latest('datetime')
#         latest_order_id = latest_order.fkmanage_id
#         # 一つ削除する
#         latest_order.delete()
#         num_2 = Order.objects.count()
#         self.assertEqual(num_1, num_2+1)
#         self.assertFalse(Order.objects.filter(fkmanage_id=latest_order_id).exists())
#         # 再びdata_migration.orderを実行すると、差分更新
#         data_migration.order()
#         num_3 = Order.objects.count()
#         self.assertEqual(num_1, num_3)
#         self.assertTrue(Order.objects.filter(fkmanage_id=latest_order_id).exists())
#         # 同じfkmanage_idは存在しない
#         unique_check = set(
#             a['c'] for a in Order.objects.exclude(fkmanage_id=None).values('fkmanage_id').annotate(c=Count('pk'))
#         )
#         self.assertEqual(set([1, ]), unique_check)
#
#     def test_stock(self):
#         # 最初はOrderが存在しない
#         self.assertFalse(Stock.objects.exists())
#         # data_migration.stock()を実行すると増える
#         data_migration.stock()
#         self.assertTrue(Stock.objects.exists())
#         num_1 = Stock.objects.count()
#         latest_stock = Stock.objects.latest('code')
#         latest_stock_code = latest_stock.code
#         # 一つ削除する
#         latest_stock.delete()
#         num_2 = Stock.objects.count()
#         self.assertEqual(num_1, num_2+1)
#         self.assertFalse(Stock.objects.filter(code=latest_stock_code).exists())
#         # 再びdata_migration.codeを実行すると、差分更新
#         data_migration.stock()
#         num_3 = Stock.objects.count()
#         self.assertEqual(num_1, num_3)
#         self.assertTrue(Stock.objects.filter(code=latest_stock_code).exists())
#         # 同じcodeは存在しない
#         unique_check = set(
#             a['c'] for a in Stock.objects.values('code').annotate(c=Count('pk'))
#         )
#         self.assertEqual(set([1, ]), unique_check)