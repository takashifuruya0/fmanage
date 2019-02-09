from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Avg, Count
# asset
from asset.models import AssetStatus

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

    def get_kakeibos(self):
        today = date.today()
        res = dict()
        data_all = self.kakeibos_set.all().order_by('-date')
        ag_all = data_all.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        res['all'] = {
            "data": data_all,
            "sum": ag_all['sum'],
            "count": ag_all['count'],
            "avg": ag_all['avg']
        }
        res['month'] = list()
        diff = relativedelta(today, data_all.last().date)
        num_month = diff.years * 12 + diff.months + 2
        date_list = [date((today - relativedelta(months=i)).year, (today - relativedelta(months=i)).month, 1) for i in range(num_month)]
        for d in date_list:
            data = self.kakeibos_set.filter(date__year=d.year, date__month=d.month).order_by('-date')
            ag = data.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
            res['month'].append(
                {
                    "date": d,
                    "data": data,
                    "sum": ag['sum'],
                    "count": ag['count'],
                    "avg": ag['avg']
                }
            )
        return res

    def get_shared(self):
        today = date.today()
        res = dict()
        res['all'] = self.sharedkakeibos_set.all().order_by('-date')
        res['month'] = self.sharedkakeibos_set.filter(date__year=today.year, date__month=today.month).order_by('-date')
        return res

    def get_credit(self):
        today = date.today()
        res = dict()
        cis = self.credititems_set.all()
        res['all'] = Credits.objects.filter(credit_item__in=cis).order_by('-date')
        res['month'] = Credits.objects.filter(credit_item__in=cis, date__month=today.month, date__year=today.year).order_by('-date')
        return res

    def sum_kakeibos(self):
        today = date.today()
        res = dict()
        res["all"] = self.kakeibos_set.all().aggregate(sum=models.Sum('fee'))['sum']
        res["month"] = self.kakeibos_set.filter(date__year=today.year, date__month=today.month).aggregate(sum=models.Sum('fee'))['sum']
        return res

    def avg_kakeibos(self):
        today = date.today()
        res = dict()
        ks = self.kakeibos_set.all()
        if ks.__len__() > 0:
            res["all"] = int(ks.aggregate(avg=models.Avg('fee'))['avg'])
        month = Kakeibos.objects.filter(usage=self, date__year=today.year, date__month=today.month)
        if month.__len__() > 0:
            res["month"] = int(month.aggregate(avg=models.Avg('fee'))['avg'])
        return res

    def sum_credit(self):
        today = date.today()
        res = {"all": 0, "month": 0}
        cis = self.credititems_set.all()
        for ci in cis:
            res["all"] += ci.sum_credit()
        res["month"] = Credits.objects.filter(date__year=today.year, date__month=today.month, credit_item__in=cis).aggregate(
            sum=models.Sum('fee'))['sum']
        return res

    def shift_kakeibos(self):
        ks = self.kakeibos_set.all()
        shift = ks.annotate(month=TruncMonth('date')).order_by('month').values('month')\
            .annotate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        return shift


class Resources(BaseModel):
    objects = None
    initial_val = models.IntegerField(null=False, blank=False)
    color = models.OneToOneField(Colors, blank=True, null=True)
    # current_val = models.IntegerField(null=True, blank=True)
    is_saving = models.BooleanField(default=False)

    def current_val(self):
        if self.name == "投資口座":
            return AssetStatus.objects.latest('date').total
        else:
            move_tos = Kakeibos.objects.filter(move_to=self)
            move_froms = Kakeibos.objects.filter(move_from=self)
            v_move_to = move_tos.aggregate(Sum('fee'))['fee__sum'] if move_tos else 0
            v_move_from = move_froms.aggregate(Sum('fee'))['fee__sum'] if move_froms else 0
            return self.initial_val + v_move_to - v_move_from


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

    # def save(self, *args, **kwargs):
    #     if self.move_from:
    #         self.move_from.current_val = self.move_from.current_val - self.fee
    #         self.move_from.save()
    #     if self.move_to:
    #         self.move_to.current_val = self.move_to.current_val + self.fee
    #         self.move_to.save()
    #     super(Kakeibos, self).save(*args, **kwargs)


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
    is_settled = models.BooleanField(default=True)

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
        if Credits.objects.filter(credit_item=self).exists():
            return Credits.objects.filter(credit_item=self).aggregate(sum=models.Sum('fee'))['sum']
        else:
            return 0

    def avg_credit(self):
        if Credits.objects.filter(credit_item=self).exists():
            return int(Credits.objects.filter(credit_item=self).aggregate(avg=models.Avg('fee'))['avg'])
        else:
            return 0

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

