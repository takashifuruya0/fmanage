from django.db import models
from .functions import get_info
from datetime import datetime, date
# Create your models here.


class Stocks(models.Model):
    objects = None
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.code) + ": " + self.name


class Orders(models.Model):
    objects = None
    datetime = models.DateTimeField(default=datetime.now, blank=True)
    order_type = models.CharField(null=False, blank=False, max_length=20)
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    num = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    commission = models.IntegerField(default=0)
    is_nisa = models.BooleanField()

    def __str__(self):
        return "S/"+str(self.datetime)+":"+self.stock.name


class HoldingStocks(models.Model):
    objects = None
    date = models.DateField()
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    num = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.stock.name

    def get_current_price(self):
        tmp = get_info.stock_overview(self.stock.code)
        if tmp['status']:
            return tmp['price']
        else:
            return self.stock.stockdatabydate_set.latest('date').val_end

    def get_holding_time(self):
        return (date.today() - self.date).days


class AssetStatus(models.Model):
    objects = None
    date = models.DateField()
    total = models.IntegerField()
    buying_power = models.IntegerField()
    stocks_value = models.IntegerField()
    other_value = models.IntegerField()
    investment = models.IntegerField()

    def get_total(self):
        return self.buying_power + self.stocks_value + self.other_value
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
    objects = None
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    date = models.DateField()
    val_start = models.FloatField()
    val_high = models.FloatField()
    val_low = models.FloatField()
    val_end = models.FloatField()
    turnover = models.IntegerField()

    def __str__(self):
        return str(self.date) + " " + self.stock.name