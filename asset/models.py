from django.db import models
from .functions import get_info
from datetime import datetime
# Create your models here.


class Stocks(models.Model):
    objects = None
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return str(self.code) + ": " +self.name


class Orders(models.Model):
    objects = None
    datetime = models.DateTimeField(default=datetime.now, blank=True)
    order_type = models.CharField(null=False, blank=False, max_length=20)
    stock = models.ForeignKey(Stocks)
    num = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    commission = models.IntegerField(default=0)
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

    def get_current_price(self):
        return get_info.stock_overview(self.code)['price']


class AssetStatus(models.Model):
    objects = None
    date = models.DateField()
    total = models.IntegerField()
    buying_power = models.IntegerField()
    stocks_value = models.IntegerField()
    other_value = models.IntegerField()
    investment = models.IntegerField()
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


class StockDataByDate(models.Model):
    stock = models.ForeignKey(Stocks)
    date = models.DateField()
    val_start = models.FloatField()
    val_high = models.FloatField()
    val_low = models.FloatField()
    val_end = models.FloatField()
    turnover = models.IntegerField()

    def __str__(self):
        return str(self.date) + " " + self.stock.name