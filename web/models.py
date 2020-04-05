from django.db import models
from datetime import date, datetime
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from web.functions import mylib_scraping
# from django.utils import timezone
import logging
logger = logging.getLogger('django')


class Stock(models.Model):
    objects = None
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)
    is_trust = models.BooleanField()
    market = models.CharField(max_length=30, blank=True, null=True)
    industry = models.CharField(max_length=30, blank=True, null=True)
    fkmanage_id = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return "({}) {}".format(self.code, self.name)

    def current_val(self):
        data = mylib_scraping.yf_detail(self.code)
        return data['data']['val'] if data['status'] else None

    def latest_val(self):
        svd = StockValueData.objects.filter(stock=self).latest('date')
        return svd.val_close if svd else None

    def save(self, *args, **kwargs):
        data = mylib_scraping.yf_detail(self.code)
        if data['status']:
            self.name = data['data']['name']
            self.market = data['data']['market']
            self.industry = data['data']['industry']
            self.is_trust = False if len(str(self.code)) == 4 else True
        return super().save(*args, **kwargs)


class StockValueData(models.Model):
    objects = None
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    val_high = models.FloatField()
    val_low = models.FloatField()
    val_open = models.FloatField()
    val_close = models.FloatField()
    turnover = models.FloatField()

    def __str__(self):
        return "{}_{}".format(self.date, self.stock)


class ReasonWinLoss(models.Model):
    objects = None
    reason = models.CharField(max_length=40)
    is_win = models.BooleanField()
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        header = "W" if self.is_win else "L"
        return "{}{}".format(header, self.reason)


class Entry(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザ")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    border_loss_cut = models.FloatField(blank=True, null=True, verbose_name="損切価格")
    border_profit_determination = models.FloatField(blank=True, null=True, verbose_name="利確価格")
    reason_win_loss = models.ForeignKey(ReasonWinLoss, on_delete=models.CASCADE, blank=True, null=True, verbose_name="理由")
    memo = models.TextField(blank=True, null=True, verbose_name="メモ")
    is_plan = models.BooleanField(default=False, verbose_name="Plan", help_text="Entry予定")
    is_closed = models.BooleanField(default=False, verbose_name="Closed", help_text="終了したEntryかどうか")
    is_simulated = models.BooleanField(default=False, verbose_name="Simulation", help_text="シミュレーション")
    is_nisa = models.BooleanField(default=False, verbose_name="NISA", help_text="NISA口座")
    num_plan = models.IntegerField(default=0, help_text="予定口数", verbose_name="予定口数")
    is_in_order = models.BooleanField(default=False, help_text="NAMSから注文中か？", verbose_name="注文中")

    def __str__(self):
        return "E{:0>3}_{}".format(self.pk, self.stock)

    def val_order(self, is_buy):
        """取引株価"""
        orders = self.order_set.filter(is_buy=is_buy)
        val = 0
        if orders.exists():
            for o in orders:
                val += (o.val * o.num)
            val = val/self.num_order(is_buy)
        return val

    def num_order(self, is_buy):
        """取引口数"""
        orders = self.order_set.filter(is_buy=is_buy)
        num = 0
        if orders.exists():
            num = orders.aggregate(num=Sum('num'))['num']
        return num

    def num_buy(self):
        """買付口数"""
        return self.num_order(is_buy=True)

    def num_sell(self):
        """売付口数"""
        return self.num_order(is_buy=False)

    def val_buy(self):
        """買付株価"""
        return self.val_order(is_buy=True)

    def val_sell(self):
        """売付株価"""
        return self.val_order(is_buy=False)

    def total_buy(self):
        """買付合計"""
        return self.val_buy() * self.num_buy()

    def total_sell(self):
        """売付合計"""
        return self.val_sell() * self.num_sell() if self.num_sell() > 0 else None

    def num_linked_orders(self):
        """紐づくOrder数"""
        return self.order_set.count()

    def remaining(self):
        """残口数"""
        return self.num_buy() - self.num_sell()

    def profit(self):
        """利益"""
        profit = 0
        for o in self.order_set.all():
            if o.is_buy:
                profit -= (o.num * o.val + o.commission)
            else:
                profit += (o.num * o.val - o.commission)
        if not self.is_closed:
            data = mylib_scraping.yf_detail(self.stock.code)
            if data['status']:
                profit += data['data']['val'] * self.remaining()
        return profit

    def profit_after_tax(self):
        """税引利益"""
        profit = self.profit()
        return round(profit * 0.8) if profit > 0 and not self.is_nisa else profit

    def profit_pct(self):
        """利益率"""
        return round(100 + self.profit() * 100 / self.val_buy() / self.num_buy(), 1) if self.order_set.exists() else 0

    def profit_profit_determination(self):
        """利確後の利益額"""
        if self.border_profit_determination:
            num = self.num_plan if self.is_plan else self.num_buy()
            val = self.stock.latest_val() if self.is_plan else self.val_buy()
            return (self.border_profit_determination - val) * num
        else:
            return None

    def profit_loss_cut(self):
        """損切後の損失額"""
        if self.border_loss_cut:
            num = self.num_plan if self.is_plan else self.num_buy()
            val = self.stock.latest_val() if self.is_plan else self.val_buy()
            return (self.border_loss_cut - val) * num
        else:
            return None

    def date_open(self):
        """EntryをOpenした日付"""
        os = self.order_set.filter(is_buy=True)
        return min([o.datetime for o in os]) if os.exists() else None

    def date_close(self):
        """EntryをCloseした日付"""
        os = self.order_set.filter(is_buy=False)
        return max([o.datetime for o in os]) if os.exists() else None

    def border_loss_cut_percent(self):
        """損切り損失率"""
        current_val = self.stock.latest_val()
        if self.border_loss_cut and current_val:
            val = current_val if self.is_plan else self.val_buy()
            return round(self.border_loss_cut / val * 100, 2)
        else:
            return None

    def border_profit_determination_percent(self):
        """利確利益率"""
        current_val = self.stock.latest_val()
        if self.border_profit_determination and current_val:
            val = current_val if self.is_plan else self.val_buy()
            return round(self.border_profit_determination / val * 100, 2)
        else:
            return None

    def save(self, *args, **kwargs):
        if self.order_set.exists():
            # check closed if remaining = 0
            self.is_plan = False
            self.is_closed = True if self.remaining() == 0 else False
            # same stocks should be linked
            for o in self.order_set.all():
                if not o.stock == self.stock:
                    raise Exception('Different stocks are linked')
            # remaining should be over 0
            if self.remaining() < 0:
                raise Exception('remaining should be over 0')
            # date_open should be earlier than date_close
            if self.is_closed and self.date_open() > self.date_close():
                raise Exception('date_open should be earlier than date_close')
        else:
            self.is_plan = True
            self.is_closed = False
        super().save(*args, **kwargs)


class Order(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.now)
    is_nisa = models.BooleanField(default=False)
    is_buy = models.BooleanField()
    is_simulated = models.BooleanField(default=False)
    num = models.IntegerField()
    val = models.FloatField()
    commission = models.IntegerField()
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=True, blank=True)
    chart = models.ImageField(upload_to='images/', null=True, blank=True)
    fkmanage_id = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        bs = "B" if self.is_buy else "S"
        return "{}_{}_{}".format(bs, self.datetime, self.stock)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.entry:
            try:
                self.entry.save()
                logger.info("{} is updated with updates of {}".format(self.entry, self))
            except Exception as e:
                logger.error(e)
                entry = self.entry
                self.entry = None
                super().save(*args, **kwargs)
                entry.save()


class AssetStatus(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    buying_power = models.IntegerField()
    investment = models.IntegerField()
    nisa_power = models.IntegerField()
    sum_stock = models.IntegerField()
    sum_trust = models.IntegerField()
    sum_other = models.IntegerField()

    def __str__(self):
        return "{}_{}".format(self.date, self.user)

    def get_total(self):
        return self.sum_other + self.sum_stock + self.sum_trust + self.buying_power

    def get_gp(self):
        return self.get_total() - self.investment

    def get_gpr(self):
        return round((self.get_total() - self.investment)/self.investment * 100, 2)

    def update_status(self):
        es = Entry.objects.filter(is_closed=False, is_plan=False)
        self.sum_stock = sum([e.remaining()*e.stock.current_val() for e in es.filter(stock__is_trust=False)])
        self.sum_trust = sum([e.remaining()*e.stock.current_val() for e in es.filter(stock__is_trust=True)])
        self.save()


class StockFinancialData(models.Model):
    objects = None
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    """ stock_settlement_info """
    interest_bearing_debt = models.FloatField(blank=True, null=True, verbose_name="有利子負債")
    roa = models.FloatField(blank=True, null=True, verbose_name="ROA")
    roe = models.FloatField(blank=True, null=True, verbose_name="ROE")
    sales = models.FloatField(blank=True, null=True, verbose_name="売上高")
    assets = models.FloatField(blank=True, null=True, verbose_name="総資産")
    eps = models.FloatField(blank=True, null=True, verbose_name="EPS")
    net_income = models.FloatField(blank=True, null=True, verbose_name="当期利益")
    bps = models.FloatField(blank=True, null=True, verbose_name="BPS")
    roa_2 = models.FloatField(blank=True, null=True, verbose_name="総資産経常利益率")
    operating_income = models.FloatField(blank=True, null=True, verbose_name="営業利益")
    equity_ratio = models.FloatField(blank=True, null=True, verbose_name="自己資本比率")
    capital = models.FloatField(blank=True, null=True, verbose_name="資本金")
    recurring_profit = models.FloatField(blank=True, null=True, verbose_name="経常利益")
    equity = models.FloatField(blank=True, null=True, verbose_name="自己資本")
    """ stock_finance_info() """
    pbr_f = models.FloatField(blank=True, null=True, verbose_name="PBR（実績）")
    eps_f = models.FloatField(blank=True, null=True, verbose_name="EPS（会社予想）")
    market_value = models.FloatField(blank=True, null=True, verbose_name="時価総額")
    per_f = models.FloatField(blank=True, null=True, verbose_name="PER（会社予想）")
    dividend_yield = models.FloatField(blank=True, null=True, verbose_name="配当利回り（会社予想）")
    bps_f = models.FloatField(blank=True, null=True, verbose_name="BPS実績")

    def __str__(self):
        return "{}_{}".format(self.date, self.stock)


class SBIAlert(models.Model):
    objects = None
    CHOICES = (
        (0, "円以上"), (1, "円以下"), (2, "％以上"), (3, "％以下"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    checked_at = models.DateTimeField(blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    val = models.IntegerField()
    type = models.IntegerField(choices=CHOICES)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}_{}".format(self.type, self.stock)

    def save(self, *args, **kwargs):
        self.is_active = False if self.checked_at else True
        return super().save(*args, **kwargs)