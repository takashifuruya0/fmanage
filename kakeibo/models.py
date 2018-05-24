from django.db import models
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


class Resources(BaseModel):
    objects = None
    initial_val = models.IntegerField(null=False, blank=False)
    color = models.OneToOneField(Colors, blank=True, null=True)


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


class Credits(models.Model):
    objects = None
    date = models.DateField()
    debit_date = models.DateField()
    fee = models.IntegerField()
    credit_item = models.ForeignKey(CreditItems)
    card = models.ForeignKey(Cards, related_name="credits", null=True)


