from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Avg, Count
from django.conf import settings
from django.utils.timezone import now
# asset
# from asset.models import AssetStatus
from web.models import AssetStatus

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
class Event(models.Model):
    objects = None
    date = models.DateField(verbose_name="日付")
    name = models.CharField(max_length=30, verbose_name="イベント名")
    memo = models.CharField(max_length=100, blank=True, null=True, verbose_name="メモ")
    detail = models.TextField(blank=True, null=True, default=None, verbose_name="詳細")
    is_active = models.BooleanField(default=True)
    sum_plan = models.IntegerField(default=0, verbose_name="計画値")

    def __str__(self):
        return "{}_{}".format(self.date, self.name)

    def sum_actual(self):
        if self.event_kakeibo.exists():
            return self.event_kakeibo.aggregate(sum=Sum('fee'))['sum']
        else:
            return 0

    def count_actual(self):
        if self.event_kakeibo.exists():
            return self.event_kakeibo.aggregate(count=Count('fee'))['count']
        else:
            return 0

    def diff_from_plan(self):
        return self.sum_actual() - self.sum_plan

    def save(self, *args, **kwargs):
        res = super().save(*args, **kwargs)
        if self.count_actual() == 0:
            Kakeibos.objects.create(
                event=self,
                date=self.date,
                memo="init",
                fee=0,
                way="その他",
                usage=Usages.objects.get(name="その他"),
                is_active=False
            )
        return res


class Colors(models.Model):
    objects = None
    name = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Usages(BaseModel):
    # objects = None
    is_expense = models.BooleanField() # 支出はTrue, 収入はFalse
    memo = models.CharField(max_length=50, blank=True, null=True)
    color = models.OneToOneField(Colors, blank=True, null=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, null=True, blank=True, help_text="FontAwesomeのHTMLタグ")

    def get_kakeibos_2(self):
        today = date.today()
        cis = self.credititems_set.all()
        res = dict()
        data_all = self.kakeibos_set.all().order_by('-date')
        ag_all = data_all.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        data_all_shared = self.sharedkakeibos_set.all().order_by('-date')
        ag_all_shared = data_all_shared.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        data_all_credit = Credits.objects.filter(credit_item__in=cis).order_by('-date')
        ag_all_credit = data_all_credit.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        res['all'] = {
            "data": data_all,
            "sum": ag_all['sum'],
            "count": ag_all['count'],
            "avg": ag_all['avg'],
            "data_shared": data_all_shared,
            "sum_shared": ag_all_shared['sum'],
            "count_shared": ag_all_shared['count'],
            "avg_shared": ag_all_shared['avg'],
            "data_credit": data_all_credit,
            "sum_credit": ag_all_credit['sum'],
            "count_credit": ag_all_credit['count'],
            "avg_credit": ag_all_credit['avg']
        }
        res['month'] = list()
        if data_all.exists() or data_all_shared.exists():
            if data_all.exists() and data_all_shared.exists():
                diff = relativedelta(today, min(data_all.last().date, data_all_shared.last().date))
            elif data_all.exists():
                diff = relativedelta(today, data_all.last().date)
            else:
                diff = relativedelta(today, data_all_shared.last().date)
            num_month = diff.years * 12 + diff.months + 2
            date_list = [date((today - relativedelta(months=i)).year, (today - relativedelta(months=i)).month, 1) for i in range(num_month)]
            for d in date_list:
                data = self.kakeibos_set.filter(date__year=d.year, date__month=d.month).order_by('-date')
                ag = data.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
                data_shared = self.sharedkakeibos_set.filter(date__year=d.year, date__month=d.month).order_by('-date')
                ag_shared = data_shared.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
                data_credit = Credits.objects.filter(date__year=d.year, date__month=d.month, credit_item__in=cis).order_by('-date')
                ag_credit = data_credit.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
                res['month'].append(
                    {
                        "date": d,
                        "data": data,
                        "sum": ag['sum'],
                        "count": ag['count'],
                        "avg": ag['avg'],
                        "data_shared": data_shared,
                        "sum_shared": ag_shared['sum'],
                        "count_shared": ag_shared['count'],
                        "avg_shared": ag_shared['avg'],
                        "data_credit": data_credit,
                        "sum_credit": ag_credit['sum'],
                        "count_credit": ag_credit['count'],
                        "avg_credit": ag_credit['avg']
                    }
                )
        return res

    def get_credit(self):
        today = date.today()
        res = dict()
        cis = self.credititems_set.all()
        data = Credits.objects.filter(credit_item__in=cis).order_by('-date')
        ag = data.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        res['all'] = {
            "data": data,
            "sum": ag['sum'],
            "avg": ag['avg'],
            "count": ag['count'],
        }
        res['month'] = list()
        diff = relativedelta(today, data.last().date)
        num_month = diff.years * 12 + diff.months + 2
        date_list = [date((today - relativedelta(months=i)).year, (today - relativedelta(months=i)).month, 1) for i in range(num_month)]
        for d in date_list:
            data_month = Credits.objects.filter(credit_item__in=cis, date__month=d.month,date__year=d.year).order_by('-date')
            ag_month = data_month.aggregate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
            res['month'].append(
                {
                    "date": d,
                    "data": data_month,
                    "sum": ag_month['sum'],
                    "avg": ag_month['avg'],
                    "count": ag_month['count'],
                }
            )
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

    def shift_kakeibo(self):
        ks = self.kakeibos_set.all()
        shift = ks.annotate(month=TruncMonth('date')).order_by('month').values('month')\
            .annotate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        return shift

    def shift_shared(self):
        ks = self.sharedkakeibos_set.all()
        shift = ks.annotate(month=TruncMonth('date')).order_by('month').values('month')\
            .annotate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        return shift

    def shift_credit(self):
        cis = self.credititems_set.all()
        cs = Credits.objects.filter(credit_item__in=cis)
        shift = cs.annotate(month=TruncMonth('date')).order_by('month').values('month')\
            .annotate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        return shift

    def __str__(self):
        return self.name


class Resources(BaseModel):
    # objects = None
    initial_val = models.IntegerField(null=False, blank=False)
    color = models.OneToOneField(Colors, blank=True, null=True, on_delete=models.CASCADE)
    is_saving = models.BooleanField(default=False, help_text="投資を除く貯金用口座")
    is_visible = models.BooleanField(default=True, help_text="DataStudioで可視化")
    is_active = models.BooleanField(default=True, help_text="Active")
    is_investment = models.BooleanField(default=False, help_text="投資用口座")

    def current_val(self):
        if self.name == "投資口座":
            return AssetStatus.objects.latest('date').get_total()
        else:
            move_tos = Kakeibos.objects.filter(move_to=self)
            move_froms = Kakeibos.objects.filter(move_from=self)
            v_move_to = move_tos.aggregate(Sum('fee'))['fee__sum'] if move_tos else 0
            v_move_from = move_froms.aggregate(Sum('fee'))['fee__sum'] if move_froms else 0
            return self.initial_val + v_move_to - v_move_from


# UsagesとResourcesの紐付け
class UsageResourceRelations(models.Model):
    objects = None
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE)
    usage = models.ForeignKey(Usages, on_delete=models.CASCADE)

    def __str__(self):
        return self.usage+"<=>"+self.resource


class Kakeibos(models.Model):
    objects = None
    # 日付
    date = models.DateField()
    # 金額
    fee = models.IntegerField()
    # 種類
    way = models.CharField(max_length=20, choices=settings.CHOICES_KAKEIBO_WAY)
    # タグ
    tag = models.CharField(max_length=100, null=True, blank=True)
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    # 使い道/収入源
    usage = models.ForeignKey(
        Usages, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動元
    move_from = models.ForeignKey(
        Resources, null=True, blank=True, related_name="move_from", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動先
    move_to = models.ForeignKey(
        Resources, null=True, blank=True, related_name="move_to", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # Event
    event = models.ForeignKey(
        Event, null=True, blank=True, default=None, related_name="event_kakeibo", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{}_{}_{}_{}".format(self.date, self.way, self.usage, self.fee)

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
    way = models.CharField(max_length=20, choices=settings.CHOICES_KAKEIBO_WAY)
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    # 使い道
    usage = models.ForeignKey(
        Usages, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動元
    move_from = models.ForeignKey(
        Resources, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 支払者
    paid_by = models.CharField(max_length=20)
    # 清算済み？
    is_settled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.way

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val


class Cards(BaseModel):
    color = models.OneToOneField(Colors, blank=True, null=True, on_delete=models.CASCADE)


class CreditItems(BaseModel):
    # objects = None
    usage = models.ForeignKey(Usages, null=True, blank=True, on_delete=models.CASCADE)
    color = models.OneToOneField(Colors, blank=True, null=True, on_delete=models.CASCADE)

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
    credit_item = models.ForeignKey(CreditItems, on_delete=models.CASCADE)
    card = models.ForeignKey(Cards, related_name="credits", null=True, on_delete=models.CASCADE)
    memo = models.CharField(null=True, blank=True, max_length=255)
    kakeibo = models.ForeignKey(Kakeibos, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "{}_{}".format(self.date, self.fee)

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val


class CronKakeibo(models.Model):
    objects = None
    # 金額
    fee = models.IntegerField()
    # 種類
    way = models.CharField(max_length=20, choices=settings.CHOICES_KAKEIBO_WAY)
    # 使い道/収入源
    usage = models.ForeignKey(
        Usages, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動元
    move_from = models.ForeignKey(
        Resources, null=True, blank=True, related_name="move_from_cron", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動先
    move_to = models.ForeignKey(
        Resources, null=True, blank=True, related_name="move_to_cron", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)


class CronShared(models.Model):
    objects = None
    # 金額
    fee = models.IntegerField()
    # 種類
    way = models.CharField(max_length=20, choices=settings.CHOICES_KAKEIBO_WAY)
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    # 使い道
    usage = models.ForeignKey(
        Usages, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動元
    move_from = models.ForeignKey(
        Resources, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 支払者
    paid_by = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)


class UsualRecord(models.Model):
    objects = None
    # 金額
    fee = models.IntegerField()
    # 種類
    way = models.CharField(max_length=20, choices=settings.CHOICES_KAKEIBO_WAY)
    # メモ
    memo = models.CharField(max_length=100, null=True, blank=True)
    # 使い道/収入源
    usage = models.ForeignKey(
        Usages, null=True, blank=True, on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動元
    move_from = models.ForeignKey(
        Resources, null=True, blank=True, related_name="ur_move_from", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # 現金移動先
    move_to = models.ForeignKey(
        Resources, null=True, blank=True, related_name="ur_move_to", on_delete=models.CASCADE,
        limit_choices_to={
            "is_active": True,
        }
    )
    # fontawesome_icon
    icon = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val


class Budget(models.Model):
    objects = None
    date = models.DateField(unique=True)
    takashi = models.IntegerField()
    hoko = models.IntegerField()
    memo = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "Budget_{}/{}".format(self.date.year, str(self.date.month).zfill(2))

    def total(self):
        return self.takashi + self.hoko


class Target(models.Model):
    CHOICES_TYPE = (
        ("総資産目標", "総資産目標"), ("投資目標", "投資目標"),
    )
    objects = None
    date = models.DateField()
    val = models.IntegerField()
    type = models.CharField(choices=settings.CHOICES_TARGET_TYPE, max_length=20)
    memo = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "{}年{}月_{}".format(self.date.year, self.date.month, self.type)