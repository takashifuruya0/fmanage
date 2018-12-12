from django.test import TestCase
from kakeibo.models import Kakeibos, SharedKakeibos, Usages, Resources, Credits, CreditItems
from django.db.models import Sum
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

    def test_usage_sum_kakeibo(self):
        today = date.today()
        usages = Usages.objects.all()
        for usage in usages:
            filtered = Kakeibos.objects.filter(usage=usage)
            # total
            total = filtered.aggregate(sum=Sum('fee'))['sum']
            total_month = filtered.filter(date__month=today.month, date__year=today.year).aggregate(sum=Sum('fee'))['sum']
            res = usage.sum_kakeibos()
            self.assertEqual(total, res['all'])
            self.assertEqual(total_month, res['month'])