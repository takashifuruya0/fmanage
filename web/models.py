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
    is_trust = models.BooleanField("投資信託", default=False)
    market = models.CharField(max_length=30, blank=True, null=True)
    industry = models.CharField(max_length=30, blank=True, null=True)
    fkmanage_id = models.IntegerField(null=True, blank=True, default=None)
    feature = models.CharField(max_length=100, blank=True, null=True, verbose_name="特色")
    consolidated_business = models.CharField(max_length=100, blank=True, null=True, verbose_name="連結事業")
    settlement_date = models.CharField(max_length=10, blank=True, null=True, verbose_name="決算月")
    unit = models.CharField(max_length=10, blank=True, null=True, verbose_name="単元株数")
    dividend = models.IntegerField(blank=True, null=True, verbose_name="配当金")
    dividend_yield = models.FloatField(blank=True, null=True, verbose_name="配当利回り")
    is_listed = models.BooleanField("上場済み", default=True)

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
        # 上場済みであれば、各種情報をスクレイピング
        data = mylib_scraping.yf_detail(self.code)
        if data['status']:
            self.name = data['data']['name']
            self.market = data['data']['market']
            self.industry = data['data']['industry']
            self.is_trust = False if len(str(self.code)) == 4 else True
            if data['data']['industry'] == "REIT":
                dividend = data['data']['financial_data']['予想分配金']
                self.dividend = None if dividend in (None, "---")  else int(float(dividend))
                dividend_yield = data['data']['financial_data']['分配金利回り']
                self.dividend_yield = None if dividend_yield in (None, "---") else dividend_yield
            elif not data['data']['industry'] == "ETF" and not self.is_trust:
                dividend = data['data']['financial_data']['1株配当']
                self.dividend = None if dividend in (None, "---") else int(float(dividend))
                dividend_yield = data['data']['financial_data']['配当利回り']
                self.dividend_yield = None if dividend_yield in (None, "---") else dividend_yield
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

    def total_now(self):
        """現在合計"""
        return self.remaining() * self.stock.current_val()

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
    date = models.DateField(verbose_name="日付")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    # prepare
    val_close_dy = models.FloatField(verbose_name="終値前日比")
    val_close_dy_pct = models.FloatField(verbose_name="終値前日比率")
    turnover_dy = models.FloatField(verbose_name="出来高前日比")
    turnover_dy_pct = models.FloatField(verbose_name="出来高前日比率")
    val_line = models.FloatField(verbose_name="ローソク長")
    val_line_pct = models.FloatField(verbose_name="ローソク長率")
    is_positive = models.BooleanField(verbose_name="陽線")
    lower_mustache = models.FloatField(verbose_name="下ヒゲ")
    upper_mustache = models.FloatField(verbose_name="上ヒゲ")
    ma05 = models.FloatField(verbose_name="移動平均（5日）")
    ma25 = models.FloatField(verbose_name="移動平均（25日）")
    ma75 = models.FloatField(verbose_name="移動平均（75日）")
    ma05_diff = models.FloatField(verbose_name="移動平均乖離（5日）", help_text="終値ー5日移動平均")
    ma25_diff = models.FloatField(verbose_name="移動平均乖離（25日）", help_text="終値ー25日移動平均")
    ma75_diff = models.FloatField(verbose_name="移動平均乖離（75日）", help_text="終値ー75日移動平均")
    ma05_diff_pct = models.FloatField(verbose_name="移動平均乖離率（5日）")
    ma25_diff_pct = models.FloatField(verbose_name="移動平均乖離率（25日）")
    ma75_diff_pct = models.FloatField(verbose_name="移動平均乖離率（75日）")
    sigma25 = models.FloatField(verbose_name="標準偏差（25日）")
    ma25_p2sigma = models.FloatField(verbose_name="ボリンジャーバンド+2σ（25日）")
    ma25_m2sigma = models.FloatField(verbose_name="ボリンジャーバンド-2σ（25日）")
    is_upper05 = models.BooleanField(verbose_name="上昇傾向（5日）", help_text="前日移動平均値より上（5日）")
    is_upper25 = models.BooleanField(verbose_name="上昇傾向（25日）", help_text="前日移動平均値より上（25日）")
    is_upper75 = models.BooleanField(verbose_name="上昇傾向（75日）", help_text="前日移動平均値より上（75日）")
    # check
    is_takuri = models.BooleanField(
        verbose_name="たくり線", help_text="長い下ヒゲ陰線", default=False
    )
    is_tsutsumi = models.BooleanField(
        verbose_name="包線", help_text="前日ローソクを包み込む、大きいローソク", default=False
    )
    is_harami = models.BooleanField(
        verbose_name="はらみ線", help_text="前日ローソクに包まれる、小さいローソク", default=False
    )
    is_age_sanpo = models.BooleanField(
        verbose_name="上げ三法", help_text="大陽線後→3本のローソクが収まる→最初の陽線終値をブレイク", default=False
    )
    is_sage_sanpo = models.BooleanField(
        verbose_name="下げ三法", help_text="大陰線後→3本のローソクが収まる→最初の陰線終値を割り込み", default=False
    )
    is_sanku_tatakikomi = models.BooleanField(
        verbose_name="三空叩き込み", help_text="3日連続の窓開き下落", default=False
    )
    is_sante_daiinsen = models.BooleanField(
        verbose_name="三手大陰線", help_text="3日連続の大陰線", default=False
    )
    svd = models.ForeignKey(StockValueData, verbose_name="SVD", null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "SAD_{}_{}".format(self.date, self.stock)

    def is_having_trend(self):
        if (self.val_close_dy_pct >= 0.05 and self.turnover_dy_pct >= 1) \
                or (self.val_close_dy_pct <= 0.05 and self.turnover_dy_pct >= 1) \
                or self.is_takuri \
                or self.is_harami \
                or self.is_tsutsumi \
                or self.is_sanku_tatakikomi \
                or self.is_age_sanpo \
                or self.is_sage_sanpo \
                or self.is_sante_daiinsen:
            return True
        else:
            return False


class AssetTarget(models.Model):
    objects = None
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新日時")
    date = models.DateField(verbose_name="日付")
    val_investment = models.IntegerField(verbose_name="予定投資元本")
    val_target = models.IntegerField(verbose_name="投資目標")
    memo = models.TextField(blank=True, null=True, verbose_name="メモ")

    def __str__(self):
        return "AssetTarget({}/{})".format(date.year, str(date.month).zfill(2))

    def is_achieved_target(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.get_total() >= self.val_target if date.today() >= self.date else None

    def is_achieved_investment(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.investment >= self.val_investment if date.today() >= self.date else None

    def actual_target(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.get_total() if date.today() >= self.date else None

    def actual_investment(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.investment

    def actual_date(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.date if date.today() >= self.date else None

    def diff_target(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.get_total() - self.val_target if date.today() >= self.date else None

    def diff_investment(self):
        astatus = AssetStatus.objects.filter(date__lte=self.date).latest('date')
        return astatus.investment - self.val_investment if date.today() >= self.date else None

    is_achieved_target.short_description = "投資目標を達成？"
    is_achieved_investment.short_description = "予定投資元本を達成？"
    actual_target.short_description = "投資実績"
    diff_target.short_description = "対投資目標差分"
    actual_investment.short_description = "投資元本実績"
    diff_investment.short_description = "対予定投資元本差分"
    actual_date.short_description = "実績日"


class Ipo(models.Model):
    # ===================================
    # CHOICES
    # ===================================
    CHOICES_RANK = (("S", "S"), ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"))
    CHOICES_STATUS = (
        ("0.起票", "0.起票"),
        ("1.評価中", "1.評価中"),
        ("2.申込済", "2.申込済"),
        ("3.落選（上場前）", "3.落選（上場前）"), ("3.当選（上場前）", "3.当選（上場前）"),
        ("4.落選（上場後）", "4.落選（上場後）"), ("4.当選（上場後）", "4.当選（上場後）"),
    )
    # ===================================
    # fields
    # ===================================
    objects = None
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name="更新日時")
    # 事前情報
    stock = models.ForeignKey(Stock, verbose_name="銘柄", on_delete=models.CASCADE)
    datetime_open = models.DateTimeField("ブックビル開始日時", blank=True, null=True)
    datetime_close = models.DateTimeField("ブックビル終了日時", blank=True, null=True)
    status = models.CharField('ステータス', max_length=255, choices=CHOICES_STATUS, default="0.起票")
    val_list = models.FloatField("発行価格", blank=True, null=True)
    date_list = models.DateField("上場日", blank=True, null=True)
    datetime_select = models.DateTimeField("抽選開始日時", blank=True, null=True)
    # 申請情報
    is_applied = models.BooleanField("申込済", default=False)
    date_applied = models.DateField("申込日", blank=True, null=True)
    num_applied = models.IntegerField("申込数", blank=True, null=True)
    point = models.IntegerField("使用ポイント数", default=None, blank=True, null=True)
    result_select = models.CharField("抽選結果", max_length=255, default="抽選待ち", blank=True, null=True)
    # 購入情報
    datetime_purchase_open = models.DateTimeField("購入意思表示開始日時", blank=True, null=True)
    datetime_purchase_close = models.DateTimeField("購入意思表示終了日時", blank=True, null=True)
    result_buy = models.CharField("購入結果", max_length=255, blank=True, null=True)
    num_select = models.IntegerField("当選数", blank=True, null=True)
    # 評判/評価 (https://96ut.com/ipo/yoso.php)
    rank = models.CharField("評価", max_length=1, choices=CHOICES_RANK, blank=True, null=True)
    val_predicted = models.FloatField("予想初値", blank=True, null=True)
    url = models.URLField("評価詳細URL", blank=True, null=True)
    # 上場後
    val_initial = models.FloatField("上場後初値", blank=True, null=True)
    entry = models.ForeignKey(Entry, verbose_name="Entry", on_delete=models.CASCADE, blank=True, null=True)
    # その他
    memo = models.TextField("メモ", blank=True, null=True)

    # ===================================
    # methods and Meta
    # ===================================
    def __str__(self):
        return "IPO_{}".format(self.stock)

    @property
    def profit_expected(self):
        if self.val_predicted and self.val_list and self.num_applied:
            return (self.val_predicted - self.val_list) * self.num_applied
        else:
            return None

    @property
    def profit_actual(self):
        if self.val_initial and self.val_list and self.num_applied:
            return (self.val_initial - self.val_list) * self.num_applied
        else:
            return None

    @property
    def profit_pct_expected(self):
        if self.val_predicted and self.val_list:
            return (self.val_predicted - self.val_list) / self.val_list * 100
        else:
            return None

    @property
    def profit_pct_actual(self):
        if self.val_initial and self.val_list:
            return (self.val_initial - self.val_list) / self.val_list * 100
        else:
            return None

    @property
    def total_applied(self):
        if self.num_applied and self.val_list:
            return self.num_applied * self.val_list
        else:
            return None

    class Meta:
        verbose_name = "IPO"
        verbose_name_plural = "IPO"


class Dividend(models.Model):
    objects = None
    entry = models.ForeignKey(Entry, verbose_name="Entry", on_delete=models.CASCADE)
    date = models.DateField("配当日")
    val_unit = models.IntegerField("配当単価")
    unit = models.IntegerField("配当単位数")
    val = models.IntegerField("配当総額（税引前）")
    tax = models.IntegerField("税額")

    class Meta:
        verbose_name = "配当"
        verbose_name_plural = "配当"

    @property
    def profit(self):
        return self.val - self.tax
