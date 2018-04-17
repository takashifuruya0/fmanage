from django.db import models

# Create your models here.


class Usages(models.Model):
    objects = None
    date = models.DateField()
    usage = models.CharField(max_length=100, unique=True)
    expense = models.BooleanField() # 支出はTrue, 収入はFalse
    color = models.CharField(max_length=30, unique=True, blank=True, null=True)

    def __str__(self):
        return self.expense_item


class Resources(models.Model):
    objects = None
    date = models.DateField()
    resources = models.CharField(max_length=100, unique=True)
    initial_val = models.IntegerField(null=False, blank=False)
    color = models.CharField(max_length=30, unique=True, blank=True, null=True)

    def __str__(self):
        return self.resources


# UsagesとResourcesの紐付け
class UsageResourceRelation(models.Model):
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
    move_from = models.ForeignKey(Resources, null=True, blank=True)
    # 現金移動先
    move_to = models.ForeignKey(Resources, null=True, blank=True)

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
    # 使い道/収入源
    usage = models.ForeignKey(Usages, null=True, blank=True)
    # 支払者
    paid_by = models.CharField(max_length=20)

    def __str__(self):
        return self.way

    def fee_yen(self):
        if self.fee >= 0:
            new_val = '¥{:,}'.format(self.fee)
        else:
            new_val = '-¥{:,}'.format(-self.fee)
        return new_val


class CreditItems(models.Model):
    objects = None
    name = models.CharField(max_length=100, unique=True)
    kind = models.CharField(max_length=20, null=True, blank=True)
    kind_key = models.ForeignKey(Usages, null=True, blank=True)

    def __str__(self):
        return self.name


class Credits(models.Model):
    objects = None
    date = models.DateField()
    debit_date = models.DateField()
    credit_item = models.ForeignKey(CreditItems)
    fee = models.IntegerField()
