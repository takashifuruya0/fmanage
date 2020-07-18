from django.db import models
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from web.functions import mylib_scraping, mylib_analysis
from django.utils import timezone
import logging
logger = logging.getLogger('django')

CHOICES_ENTRY_TYPE = (
    ("短期", "短期"), ("中期", "中期"), ("長期", "長期"),
)


class Stock(models.Model):
    objects = None
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新日時")
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=40)
    is_trust = models.BooleanField()
    market = models.CharField(max_length=30, blank=True, null=True)
    industry = models.CharField(max_length=30, blank=True, null=True)
    fkmanage_id = models.IntegerField(null=True, blank=True, default=None)
    feature = models.CharField(max_length=100, blank=True, null=True, verbose_name="特色")
    consolidated_business = models.CharField(max_length=100, blank=True, null=True, verbose_name="連結事業")
    settlement_date = models.CharField(max_length=10, blank=True, null=True, verbose_name="決算月")
    unit = models.CharField(max_length=10, blank=True, null=True, verbose_name="単元株数")
    dividend = models.IntegerField(blank=True, null=True, verbose_name="配当金")
    dividend_yield = models.FloatField(blank=True, null=True, verbose_name="配当利回り")

    def __str__(self):
        return "({}) {}".format(self.code, self.name)

    def current_val(self):
        data = mylib_scraping.yf_detail(self.code)
        return data['data']['val'] if data['status'] else self.latest_val()

    def latest_val(self):
        svd = StockValueData.objects.filter(stock=self).latest('date')
        return svd.val_close if svd else None

    def latest_val_date(self):
        svd = StockValueData.objects.filter(stock=self).latest('date')
        return svd.date if svd else None

    def analysis(self, days=30):
        print(self)
        target_date = date.today() - relativedelta(days=days)
        svds = StockValueData.objects.filter(stock=self, date__gte=target_date).order_by('date')
        if svds.count() > 1:
            analysis = mylib_analysis.prepare(svds)
            return analysis.iloc[-1]
        else:
            return None

    def save(self, *args, **kwargs):
        data = mylib_scraping.yf_detail(self.code)
        if data['status']:
            self.name = data['data']['name']
            self.market = data['data']['market']
            self.industry = data['data']['industry']
            self.is_trust = False if len(str(self.code)) == 4 else True
            if data['data']['industry'] == "REIT":
                dividend = data['data']['financial_data']['予想分配金']
                self.dividend = dividend if dividend is None else int(float(dividend))
                self.dividend_yield = data['data']['financial_data']['分配金利回り']
            elif not data['data']['industry'] == "ETF" and not self.is_trust:
                dividend = data['data']['financial_data']['1株配当（会社予想）']
                self.dividend = dividend if dividend is None else int(float(dividend))
                self.dividend_yield = data['data']['financial_data']['配当利回り（会社予想）']
        profile = mylib_scraping.yf_profile(self.code)
        if profile['status']:
            self.feature = profile['data']["特色"]
            self.consolidated_business = profile['data']["連結事業"]
            self.settlement_date = profile['data']["決算"]
            self.unit = profile['data']["単元株数"]
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


class EntryStatus(models.Model):
    objects = None
    status = models.CharField(max_length=20)
    entry_type = models.CharField(
        choices=CHOICES_ENTRY_TYPE, max_length=10, verbose_name="Entry種別",
        null=True, blank=True
    )
    definition = models.CharField(max_length=100)
    min_profit_percent = models.FloatField(help_text="足切り利益率", blank=True, null=True)
    max_holding_period = models.IntegerField(help_text="最大保有期間", blank=True, null=True)
    is_within_week = models.BooleanField(help_text="週跨ぎしないEntry")
    is_within_holding_period = models.BooleanField(default=True, help_text="保有期間超えを許容しない")
    is_for_plan = models.BooleanField(default=False, help_text="Plan向けステータス")

    def __str__(self):
        return self.status


class Entry(models.Model):
    objects = None
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新日時")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ユーザ")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, verbose_name="銘柄")
    border_loss_cut = models.FloatField(blank=True, null=True, verbose_name="損切価格")
    border_profit_determination = models.FloatField(blank=True, null=True, verbose_name="利確価格")
    reason_win_loss = models.ForeignKey(ReasonWinLoss, on_delete=models.CASCADE, blank=True, null=True, verbose_name="理由")
    memo = models.TextField(blank=True, null=True, verbose_name="メモ")
    is_plan = models.BooleanField(default=False, verbose_name="EntryPlan", help_text="EntryPlanかどうか")
    is_closed = models.BooleanField(default=False, verbose_name="Closed", help_text="終了したEntryかどうか")
    is_simulated = models.BooleanField(default=False, verbose_name="Simulation", help_text="シミュレーション")
    is_nisa = models.BooleanField(default=False, verbose_name="NISA", help_text="NISA口座")
    num_plan = models.IntegerField(default=0, verbose_name="予定口数")
    val_plan = models.FloatField(blank=True, null=True, verbose_name="予定Entry株価")
    is_in_order = models.BooleanField(default=False, help_text="NAMSから注文中か？", verbose_name="注文中")
    entry_type = models.CharField(choices=CHOICES_ENTRY_TYPE, max_length=10, verbose_name="Entry種別", default="中期")
    status = models.ForeignKey(EntryStatus, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.is_plan:
            head = 'I' if self.is_closed else 'P'
        else:
            head = 'C' if self.is_closed else 'O'
        return "{}{:0>3}_{}".format(head, self.pk, self.stock)

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

    def total_plan(self):
        """Plan合計"""
        return self.val_plan * self.num_plan if self.val_plan else None

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
        # return round(self.profit() * 100 / self.val_buy() / self.num_buy(), 1) if self.order_set.exists() else 0
        return self.profit() / self.val_buy() / self.num_buy() if self.order_set.exists() else 0

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
            return round(self.border_loss_cut / val * 100 - 100, 2)
        else:
            return None

    def border_profit_determination_percent(self):
        """利確利益率"""
        current_val = self.stock.latest_val()
        if self.border_profit_determination and current_val:
            val = current_val if self.is_plan else self.val_buy()
            return round(self.border_profit_determination / val * 100 - 100, 2)
        else:
            return None

    def holding_period(self):
        """保有期間。Planの場合はNoneを返す"""
        if self.is_plan:
            return None
        else:
            days = ((self.date_close() if self.is_closed else datetime.now(timezone.utc)) - self.date_open()).days
            return days + 1

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
            # self.is_closed = False
        super().save(*args, **kwargs)

    def profit_per_days(self):
        """利益/保有期間"""
        return self.profit() / self.holding_period()


class Order(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.now)
    is_nisa = models.BooleanField(default=False)
    is_buy = models.BooleanField()
    is_simulated = models.BooleanField(default=False)
    num = models.IntegerField()
    val = models.FloatField(help_text="株価/投資信託単価")
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
        """合計の算出"""
        return self.sum_other + self.sum_stock + self.sum_trust + self.buying_power

    def get_gp(self):
        """粗利の算出"""
        return self.get_total() - self.investment

    def get_gpr(self):
        """粗利(%)の算出"""
        return round((self.get_total() - self.investment)/self.investment * 100, 2)

    def update_status(self):
        """Entryに従って、sum_stock, sum_trustの更新"""
        es = Entry.objects.filter(is_closed=False, is_plan=False)
        try:
            self.sum_stock = 0
            self.sum_trust = 0
            for e in es:
                current_val = e.stock.current_val()
                val = current_val if current_val else e.stock.latest_val()
                num = e.remaining()
                total = val * num
                if e.stock.is_trust:
                    self.sum_trust += total
                else:
                    self.sum_stock += total
            self.save()
            logger.info("{}.update_status() was completed successfully".format(self))
            return True
        except Exception as err:
            logger.error(err)
            return False


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


class StockAnalysisData(models.Model):
    objects = None
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新日時")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    val_close_diff = models.FloatField(verbose_name="終値前日比")
    val_close_diff_pct = models.FloatField(verbose_name="終値前日比率")
    turnover_diff = models.FloatField(verbose_name="出来高前日比")
    turnover_diff_pct = models.FloatField(verbose_name="出来高前日比率")
    val_line = models.FloatField(verbose_name="線長")
    is_positive = models.BooleanField(verbose_name="陽線")
    lower_mustache = models.FloatField(verbose_name="下ヒゲ")
    upper_mustache = models.FloatField(verbose_name="上ヒゲ")
    ma05 = models.FloatField(verbose_name="移動平均（5日）")
    ma25 = models.FloatField(verbose_name="移動平均（25日）")
    ma75 = models.FloatField(verbose_name="移動平均（75日）")
    ma05_diff = models.FloatField(verbose_name="移動平均乖離（5日）")
    ma25_diff = models.FloatField(verbose_name="移動平均乖離（25日）")
    ma75_diff = models.FloatField(verbose_name="移動平均乖離（75日）")
    ma05_diff_pct = models.FloatField(verbose_name="移動平均乖離率（5日）")
    ma25_diff_pct = models.FloatField(verbose_name="移動平均乖離率（25日）")
    ma75_diff_pct = models.FloatField(verbose_name="移動平均乖離率（75日）")
    sigma_25 = models.FloatField(verbose_name="ボリンジャーバンド（25日）")
    ma_25p2sigma = models.FloatField(verbose_name="ボリンジャーバンド上線（25日）")
    ma_25m2sigma = models.FloatField(verbose_name="ボリンジャーバンド下線（25日）")
    is_upper05 = models.BooleanField(verbose_name="上昇傾向（5日）")
    is_upper25 = models.BooleanField(verbose_name="上昇傾向（25日）")
    is_upper75 = models.BooleanField(verbose_name="上昇傾向（75日）")
