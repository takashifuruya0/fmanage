from django.db import models

# Create your models here.


class Stocks(models):
    objects = None
    name = models.CharField()
    code = models.CharField()

    def __str__(self):
        return self.name


class HoldingStocks(models):
    objects = None
    date = models.DateField()
    stock = models.ForeignKey(Stocks)
    num = models.IntegerField()

    def __str__(self):
        return self.stock.name + "/" + self.num


class BuyOrders(models):
    objects = None
    datetime = models.DateTimeField()
    stock = models.ForeignKey(Stocks)
    num = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    commission = models.IntegerField()

    def __str__(self):
        return "B/"+self.datetime+":"+self.stock


class SellOrders(models):
    objects = None
    datetime = models.DateTimeField()
    stock = models.ForeignKey(Stocks)
    num = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    commission = models.IntegerField()

    def __str__(self):
        return "S/"+self.datetime+":"+self.stock


class Results(models):
    buyorder = models.ForeignKey(BuyOrders)
    sellorder = models.ForeignKey(SellOrders)
    holding_time = models.IntegerField()
    result = models.IntegerField()

    def __str__(self):
        return self.buyorder+":"+self.sellorder



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
