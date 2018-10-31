from django.db import models
from .functions import get_info
# Create your models here.


class Stocks(models.Model):
    objects = None
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


# class BuyOrders(models.Model):
#     objects = None
#     datetime = models.DateTimeField()
#     stock = models.ForeignKey(Stocks)
#     num = models.IntegerField(null=False, blank=False)
#     price = models.FloatField(null=False, blank=False)
#     commission = models.IntegerField()  # 手数料
#     is_nisa = models.BooleanField()
#
#     def __str__(self):
#         return "B/"+str(self.datetime)+":"+self.stock
#
#
# class SellOrders(models.Model):
#     objects = None
#     datetime = models.DateTimeField()
#     stock = models.ForeignKey(Stocks)
#     num = models.IntegerField(null=False, blank=False)
#     price = models.FloatField(null=False, blank=False)
#     commission = models.IntegerField()
#     is_nisa = models.BooleanField()
#
#     def __str__(self):
#         return "S/"+str(self.datetime)+":"+self.stock


class Orders(models.Model):
    objects = None
    datetime = models.DateTimeField()
    order_type = models.CharField(null=False, blank=False, max_length=20)
    stock = models.ForeignKey(Stocks)
    num = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    commission = models.IntegerField()
    is_nisa = models.BooleanField()

    def __str__(self):
        return "S/"+str(self.datetime)+":"+self.stock.name


class HoldingStocks(models.Model):
    objects = None
    date = models.DateField()
    stock = models.ForeignKey(Stocks)
    num = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.stock.name


class AssetStatus(models.Model):
    objects = None
    date = models.DateField()
    total = models.IntegerField()
    buying_power = models.IntegerField()
    stocks_value = models.IntegerField()
    other_value = models.IntegerField()
    investment = models.IntegerField()

# class Results(models.Model):
#     buy_order = models.ForeignKey(BuyOrders)
#     sell_order = models.ForeignKey(SellOrders)
#     holding_time = models.IntegerField()
#     result = models.IntegerField()
#
#     def __str__(self):
#         return self.buy_order + ":" + self.sell_order



    # 国内株式約定通知
    # ----------------
    # 約定日時
    # 2018 - 03 - 06
    # 14: 12
    # 注文番号
    # 290
    # 現物買
    # 銘柄
    # 1571
    # 日経インバＥＴＦ
    # ＰＴＳ
    # 株数: 120
    # 価格: 1, 738
