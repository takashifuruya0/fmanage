from django.db import models
from .functions import get_info
from datetime import datetime, date
# Create your models here.


class Stocks(models.Model):
    objects = None
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=100)
    market = models.CharField(max_length=30, default=None, null=True)
    industry = models.CharField(max_length=30, default=None, null=True)

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
    chart = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return "S/"+str(self.datetime)+":"+self.stock.name

    def get_chart(self):
        if self.chart:
            return True
        import requests
        from io import BytesIO
        from django.core import files
        try:
            url_chart = "https://chart.yahoo.co.jp/?code={}.T&tm=6m&type=c&log=off&size=m&over=m25,m75&add=m,r,vm&comp=".format(
                self.stock.code)
            r = requests.get(url_chart)
            if r.status_code == 200:
                # file
                filename = "{}_{}.png".format(self.datetime.date(), self.stock.code)
                fp = BytesIO()
                fp.write(r.content)
                self.chart.save(filename, files.File(fp))
            return True
        except Exception as e:
            return False


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


class ReasonLose(models.Model):
    objects = None
    name = models.CharField(max_length=30)


class EntryExit(models.Model):
    objects = None
    # Stock
    stock = models.ForeignKey(Stocks)
    # Entry
    date_entry = models.DateField()
    chart_entry = models.ImageField(upload_to='images/')
    price_entry = models.FloatField()
    num_entry = models.IntegerField()
    # 利益確定・損切り価格
    price_set_profit = models.FloatField()
    price_loss_cut = models.FloatField()
    # Exit
    date_exit = models.DateField(null=True, blank=True)
    chart_exit = models.ImageField(blank=True, upload_to='images/')
    price_exit = models.FloatField(null=True, blank=True)
    num_exit = models.IntegerField(null=True, blank=True)
    # 手数料
    commission = models.IntegerField(default=0)
    # 敗因
    reason_lose = models.ForeignKey(ReasonLose, null=True, blank=True)
    # Memo
    memo = models.TextField(null=True, blank=True)


# class EntryType(models.Model):
#     objects = None
#     name = models.CharField(max_length=20)
#
#
# class OrderPlan(models.Model):
#     objects = None
#     # Stock
#     stock = models.ForeignKey(Stocks)
#     # Plan
#     date = models.DateField()
#     num = models.IntegerField()
#     price = models.FloatField()
#     entry_type = models.ForeignKey(EntryType)
#     # 利益確定・損切り価格
#     price_set_profit = models.FloatField()
#     price_loss_cut = models.FloatField()
#     # Entry
#     date_entry = models.DateField()
#     chart_entry = models.ImageField(upload_to='images/')
#     price_entry = models.FloatField()
#     # Exit
#     date_exit = models.DateField(null=True, blank=True)
#     chart_exit = models.ImageField(blank=True, upload_to='images/')
#     price_exit = models.FloatField(null=True, blank=True)
#     # 敗因
#     reason_lose = models.ForeignKey(ReasonLose, null=True, blank=True)
#     # Memo
#     memo = models.TextField(null=True, blank=True)

# class StockFinancialInfo(models.Model):
#     objects = None
#     stock = models.ForeignKey(Stocks)
#     date = models.DateField()
#     """ stock_settlement_info """
#     # 有利子負債
#     interest_bearing_debt = models.IntegerField(blank=True, null=True)
#     # ROA（総資産利益率）
#     roa = models.FloatField(blank=True, null=True)
#     # ROE
#     roe = models.FloatField(blank=True, null=True)
#     # 売上高
#     sales = models.IntegerField(blank=True, null=True)
#     # 総資産
#     assets = models.IntegerField(blank=True, null=True)
#     # EPS
#     eps = models.FloatField(blank=True, null=True)
#     # 当期利益
#     net_income = models.IntegerField(blank=True, null=True)
#     bps = models.FloatField(blank=True, null=True)
#     # 総資産経常利益率
#     roa_2 = models.FloatField(blank=True, null=True)
#     # 営業利益
#     operating_income = models.IntegerField(blank=True, null=True)
#     # 自己資本比率
#     equity_ratio = models.FloatField(blank=True, null=True)
#     # 資本金
#     capital = models.IntegerField(blank=True, null=True)
#     # 経常利益
#     recurring_ratio = models.IntegerField(blank=True, null=True)
#     # 自己資本
#     equity = models.IntegerField(blank=True, null=True)
#
#     """ stock_finance_info() """
#     # PBR（実績）
#     pbr_f = models.FloatField(blank=True, null=True)
#     # EPS（会社予想）
#     eps_f = models.FloatField(blank=True, null=True)
#     # 時価総額
#     market_value = models.IntegerField(blank=True, null=True)
#     # PER（会社予想）
#     per_f = models.FloatField(blank=True, null=True)
#     # 配当利回り
#     dividend_yield = models.FloatField(blank=True, null=True)
#     # BPS（実績）
#     bps_f = models.FloatField(blank=True, null=True)
#
#     def __str__(self):
#         return "{}:{}".format(self.date, self.stock.name)