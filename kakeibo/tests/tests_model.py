from django.test import TestCase
from kakeibo.models import *
from dateutil.relativedelta import relativedelta
from datetime import date


class ModelTest(TestCase):
    num_kakeibo = 10
    num_usage = 3
    num_resource = 3

    def setUp(self):
        today = date.today()
        for i in range(self.num_resource):
            Resources.objects.create(
                name="resource"+str(i),
                date=today,
                initial_val=i*10000
            )
        for i in range(self.num_usage):
            is_expense = False if i==2 else True
            Usages.objects.create(
                name="usage"+str(i),
                date=today,
                is_expense=is_expense
            )
        ways = ["支出（現金）", "振替", "収入"]
        usages = [u for u in Usages.objects.all()]
        for i in range(self.num_kakeibo):
            Kakeibos.objects.create(
                fee=i*100,
                date=today,
                way=ways[i%ways.__len__()],
                usage=usages[i%usages.__len__()]
            )

    def test_kakeibo(self):
        c = Kakeibos.objects.all().count()
        self.assertEqual(c, self.num_kakeibo)

    def test_budget(self):
        # Budget作成
        takashi = 90000
        hoko = 60000
        b = Budget.objects.create(takashi=takashi, hoko=hoko, date=date.today())
        self.assertEqual(Budget.objects.count(), 1)
        # sum取得
        self.assertEqual(b.total(), takashi+hoko)
        # 違う年月のBudgetは作成できる
        b2 = Budget.objects.create(takashi=takashi, hoko=hoko, date=date.today() + relativedelta(months=1))
        self.assertEqual(Budget.objects.count(), 2)
        # 同じ年月のbudgetは作成できない
        try:
            b1 = Budget.objects.create(takashi=takashi, hoko=hoko, date=date.today())
            self.fail("同じ年月のbudgetは作成できない")
        except Exception as e:
            pass
