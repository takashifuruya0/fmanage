from django.contrib import admin
from django import forms
from .models import Stock, StockFinancialData, AssetStatus
from .models import StockValueData, Order, Entry, ReasonWinLoss
from .models import SBIAlert, EntryStatus, StockAnalysisData, AssetTarget
from .models import Ipo, Dividend
from .functions import mylib_asset
from .forms import OrderForm
from django.contrib import messages
from web.forms import StockAnalysisDataForm
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats


# Register your models here.
class StockAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'is_trust', 'code', 'name', 'market', 'industry',
        "dividend", "dividend_yield", "fkmanage_id",
        "created_at", "updated_at",
    ]
    list_filter = ['market', 'industry', ]
    search_fields = ['is_trust', 'code', 'name', ]


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = [
        'pk', "user", "date",
        "buying_power", "sum_stock", "sum_other", "sum_trust",
        "investment", "get_total",
    ]
    list_filter = ["user", "date", ]


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "is_buy", "is_nisa",
        "user", "datetime", "entry", "stock",
        "num", "val", "commission",
        "chart", "fkmanage_id",
    ]
    list_filter = [
        "user", "datetime", "is_buy", "stock__is_trust",
        "stock__name", "stock__code", "stock__industry", "stock__market",
    ]
    search_fields = ['stock__name']
    actions = ["do_order_process", ]
    form = OrderForm

    def chart_image(self, row):
        if row.chart:
            return '<img src="/document/{}" style="width:100px;height:auto;">'.format(row.chart)
        else:
            return None

    def do_order_process(self, request, queryset):
        for o in queryset.order_by('datetime'):
            res = mylib_asset.order_process(o, o.user)
            if res['status']:
                messages.success(request, "Done")
            else:
                messages.error(request, "error")

    do_order_process.short_description = "OrderProcessの実行"
    chart_image.allow_tags = True


class StockValueDataAdmin(admin.ModelAdmin):
    list_display = ['pk', "stock", "date", "val_open", "val_high", "val_low", "val_close", "turnover"]
    list_filter = ["stock__code", "stock__name", "stock__industry", "stock__market", "date", ]
    search_fields = ['stock__name']


class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'created_at', 'updated_at', 'stock',
        'is_closed', 'is_simulated', "is_plan",
        "remaining", "profit",
        'reason_win_loss', 'memo', "num_linked_orders",
    ]
    list_filter = [
        "is_closed", "is_simulated", "is_plan",
        "stock__name",
        "stock__code",
        "stock__industry", "stock__market",
    ]
    search_fields = ['stock__name']


class StockFinancialDataAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'stock', 'date',
        'assets',
        'eps', 'roe', 'roa', 'roa_2', 'bps',
        'pbr_f', 'per_f', 'eps_f', 'bps_f',
        'capital', 'sales',
        'equity', 'equity_ratio',
        'net_income',
        'recurring_profit',
        'operating_income',
        'dividend_yield', 'market_value',
        'interest_bearing_debt',
    ]
    list_filter = ['date', "stock__name", "stock__code", "stock__industry", "stock__market", ]
    search_fields = ['stock__name']


class ReasonWinLossAdmin(admin.ModelAdmin):
    list_display = ["pk", "reason", "is_win", ]


class SBIAlertAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "created_at", "checked_at",
        "stock", "val", "type", "is_active"
    ]


class EntryStatusAdmin(admin.ModelAdmin):
    list_display = [
        "status", "min_profit_percent", "max_holding_period",
        "is_within_week", "is_within_holding_period", "is_for_plan",
    ]
    list_editable = [
        "is_within_week", "is_within_holding_period", "is_for_plan",
    ]


class StockAnalysisDataAdmin(admin.ModelAdmin):
    list_display = [
        "stock", "date", "created_at", "updated_at",
        "val_close_dy_pct_100", "turnover_dy_pct_100",
    ]
    search_fields = ["stock__code", "stock__name", ]
    list_filter = [
        "date", "is_harami", "is_takuri", "is_tsutsumi", "is_age_sanpo",
        "is_sage_sanpo", "is_sante_daiinsen", "is_sanku_tatakikomi",
    ]
    form = StockAnalysisDataForm

    def val_close_dy_pct_100(self, row):
        return "{}%".format(round(row.val_close_dy_pct * 100, 2))

    def turnover_dy_pct_100(self, row):
        return "{}%".format(round(row.turnover_dy_pct * 100, 2))

    val_close_dy_pct_100.short_description = "終値前日比（%）"
    turnover_dy_pct_100.short_description = "出来高前日比（%）"


class AssetTargetResource(resources.ModelResource):
    class Meta:
        model = AssetTarget


class AssetTargetAdmin(ImportExportModelAdmin):
    list_display = [
        "id", "date", "val_investment", "val_target",
        "is_achieved_target", "actual_target", "diff_target",
        "created_at", "updated_at",
    ]
    list_editable = ["date", "val_investment", "val_target", ]
    list_filter = ["date", ]
    resource_class = AssetTargetResource
    formats = [base_formats.XLSX]


class IpoAdmin(admin.ModelAdmin):
    list_display = [
        "pk", "stock", "rank",
        "datetime_open", "datetime_close", "is_applied", "total_applied",
        "datetime_select", "result_select"
    ]
    ordering = ["-datetime_close", ]
    list_filter = ("is_applied", )


class DividendAdmin(admin.ModelAdmin):
    list_display = ["pk", "date", "entry", "val"]
    autocomplete_fields = ("entry", )


admin.site.register(Stock, StockAdmin)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(StockValueData, StockValueDataAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(StockFinancialData, StockFinancialDataAdmin)
admin.site.register(ReasonWinLoss, ReasonWinLossAdmin)
admin.site.register(SBIAlert, SBIAlertAdmin)
admin.site.register(EntryStatus, EntryStatusAdmin)
admin.site.register(StockAnalysisData, StockAnalysisDataAdmin)
admin.site.register(AssetTarget, AssetTargetAdmin)
admin.site.register(Ipo, IpoAdmin)
admin.site.register(Dividend, DividendAdmin)
