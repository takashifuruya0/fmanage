from django.contrib import admin
from .models import *


# Register your models here.
class StocksAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'market', 'industry']
    list_filter = ['market', 'industry']
    search_fields = ['name']


class HoldingStocksAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', "get_holding_time", 'stock', 'num', 'price', 'get_current_price']
    list_filter = ['date', 'stock__name']


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ["date", "total", "buying_power", "stocks_value", "other_value", "investment", "get_total"]
    list_filter = ['date', ]


class OrdersAdmin(admin.ModelAdmin):
    list_display = ["datetime", "order_type", "stock", "num", "price", "commission", "is_nisa", "chart", "chart_image"]
    list_filter = ['datetime', 'order_type', "stock__name"]

    def chart_image(self, row):
        if row.chart:
            return '<img src="/document/{}" style="width:100px;height:auto;">'.format(row.chart)
        else:
            return None

    chart_image.allow_tags = True


class StockDataByDateAdmin(admin.ModelAdmin):
    list_display = ["stock", "date", "val_start", "val_high", "val_low", "val_end", "turnover"]
    list_filter = ["stock__name", "date", ]


class EntryExitAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'stock', 'date_entry', 'chart_entry',
        'num_entry', 'price_entry', 'price_set_profit', 'price_loss_cut',
        'date_exit', 'num_exit', 'chart_exit', 'price_exit', 'reason_lose',
        'memo', 'commission',
    ]


class StockFinancialInfoAdmin(admin.ModelAdmin):
    list_display = [
        'stock', 'date',
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
    list_filter = ['date', "stock__name"]
    search_fields = ['stock__name']


admin.site.register(Stocks, StocksAdmin)
admin.site.register(HoldingStocks, HoldingStocksAdmin)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(StockDataByDate, StockDataByDateAdmin)
admin.site.register(EntryExit, EntryExitAdmin)
admin.site.register(StockFinancialInfo, StockFinancialInfoAdmin)