from django.db import models
from datetime import date
# Create your models here.
# ==============================
#            Base
# ==============================


class BaseModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    date = models.DateField()

    def __str__(self):
        return self.name

# ==============================
#            model
# ==============================


class Colors(models.Model):
    objects = None
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Usages(BaseModel):
    objects = None
    is_expense = models.BooleanField() # 支出はTrue, 収入はFalse
    color = models.OneToOneField(Colors, blank=True, null=True)

    def check_kakeibo(self):
        today = date.today()
        if Kakeibos.objects.filter(usage=self).__len__() == 0:
            res = {"month": False, "all": False, }
        elif Kakeibos.objects.filter(usage=self, date__month=today.month, date__year=today.year).__len__() == 0:
            res = {"month": False, "all": True, }
        else:
            res = {"month": True, "all": True, }
        return res

    def check_shared(self):
        today = date.today()
        if SharedKakeibos.objects.filter(usage=self).__len__() == 0:
            res = {"month": False, "all": False, }
        elif SharedKakeibos.objects.filter(usage=self, date__month=today.month, date__year=today.year).__len__() == 0:
            res = {"month": False, "all": True, }
        else:
            res = {"month": True, "all": True, }
        return res

    def check_credit(self):
        today = date.today()
        cis = CreditItems.objects.filter(usage=self)
        if Credits.objects.filter(credit_item__in=cis).__len__() == 0:
            res = {"month": False, "all": False, }
        elif Credits.objects.filter(credit_item__in=cis, date__month=today.month, date__year=today.year).__len__() == 0:
            res = {"month": False, "all": True, }
        else:
            res = {"month": True, "all": True, }
        return res

    def get_kakeibos(self):
        today = date.today()
        res = dict()
        res['all'] = Kakeibos.objects.filter(usage=self).order_by('-date')
        res['month'] = Kakeibos.objects\
            .filter(usage=self, date__year=today.year, date__month=today.month).order_by('-date')
        return res

    def get_shared(self):
        today = date.today()
        res = dict()
        res['all'] = SharedKakeibos.objects.filter(usage=self).order_by('-date')
        res['month'] = SharedKakeibos.objects\
            .filter(usage=self, date__year=today.year, date__month=today.month).order_by('-date')
        return res

    def get_credit_items(self):
        return CreditItems.objects.filter(usage=self)

    def sum_kakeibos(self):
        today = date.today()
        res = dict()
        res["all"] = Kakeibos.objects.filter(usage=self).aggregate(sum=models.Sum('fee'))['sum']
        res["month"] = Kakeibos.objects.filter(usage=self, date__year=today.year, date__month=today.month).aggregate(sum=models.Sum('fee'))['sum']
        return res

    def avg_kakeibos(self):
        today = date.today()
        res = dict()
        ks = Kakeibos.objects.filter(usage=self)
        if ks.__len__() > 0:
            res["all"] = int(ks.aggregate(avg=models.Avg('fee'))['avg'])
        month = Kakeibos.objects.filter(usage=self, date__year=today.year, date__month=today.month)
        if month.__len__() > 0:
            res["month"] = int(month.aggregate(avg=models.Avg('fee'))['avg'])
        return res

    def sum_credits(self):
        today = date.today()
        res = {"all": 0, "month": 0}
        cis = CreditItems.objects.filter(usage=self)
        for ci in cis:
            res["all"] += ci.sum_credit()
        res["month"] = Credits.objects.filter(date__year=today.year, date__month=today.month, credit_item__in=cis).aggregate(
            sum=models.Sum('fee'))['sum']

        return res


class Resources(BaseModel):
    objects = None
    initial_val = models.IntegerField(null=False, blank=False)
    color = models.OneToOneField(Colors, blank=True, null=True)
    current_val = models.IntegerField(null=True, blank=True)


# UsagesとResourcesの紐付け
class UsageResourceRelations(models.Model):
    objects = None
    resource = models.ForeignKey(Resources)
    usage = models.ForeignKey(Usages)

    def __str__(self):
        return self.usage+"<=>"+self.resource


class Kakeibos(models.Model):
    objects = None
    # 日付
    date = models.DateField()
    # 金額
    fee = models.IntegerField()
    # 種類
    way = models.CharField(max_length=20)
    # タグ
    tag = models.CharField(max_length=100, null=True, blank=True)
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    # 使い道/収入源
    usage = models.ForeignKey(Usages, null=True, blank=True)
    # 現金移動元
    move_from = models.ForeignKey(Resources, null=True, blank=True, related_name="move_from")
    # 現金移動先
    move_to = models.ForeignKey(Resources, null=True, blank=True, related_name="move_to")

    def __str__(self):
        return self.way

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val


class SharedKakeibos(models.Model):
    objects = None
    # 日付
    date = models.DateField()
    # 金額
    fee = models.IntegerField()
    # 種類
    way = models.CharField(max_length=20)
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    # 使い道
    usage = models.ForeignKey(Usages, null=True, blank=True)
    # 現金移動元
    move_from = models.ForeignKey(Resources, null=True, blank=True)
    # 支払者
    paid_by = models.CharField(max_length=20)
    # 清算済み？
    is_settled = models.BooleanField()

    def __str__(self):
        return self.way

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val


class Cards(BaseModel):
    color = models.OneToOneField(Colors, blank=True, null=True)


class CreditItems(BaseModel):
    objects = None
    usage = models.ForeignKey(Usages, null=True, blank=True)
    color = models.OneToOneField(Colors, blank=True, null=True)

    def count_credit(self):
        return Credits.objects.filter(credit_item=self).__len__()

    def sum_credit(self):
        return Credits.objects.filter(credit_item=self).aggregate(sum=models.Sum('fee'))['sum']

    def avg_credit(self):
        return int(Credits.objects.filter(credit_item=self).aggregate(avg=models.Avg('fee'))['avg'])

    def get_credits(self):
        return Credits.objects.filter(credit_item=self).order_by('-date')


class Credits(models.Model):
    objects = None
    date = models.DateField()
    debit_date = models.DateField()
    fee = models.IntegerField()
    credit_item = models.ForeignKey(CreditItems)
    card = models.ForeignKey(Cards, related_name="credits", null=True)
    memo = models.CharField(null=True, blank=True, max_length=255)

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val

