from django.contrib import admin
from .models import *


# Register your models here.
class StocksAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']


class HoldingStocksAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', "get_holding_time", 'stock', 'num', 'price', 'get_current_price']


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ["date", "total", "buying_power", "stocks_value", "other_value", "investment", "get_total"]


class OrdersAdmin(admin.ModelAdmin):
    list_display = ["datetime", "order_type", "stock", "num", "price", "commission", "is_nisa", "chart", "chart_image"]

    def chart_image(self, row):
        if row.chart:
            return '<img src="/document/{}" style="width:100px;height:auto;">'.format(row.chart)
        else:
            return None

    chart_image.allow_tags = True


class StockDataByDateAdmin(admin.ModelAdmin):
    list_display = ["stock", "date", "val_start", "val_high", "val_low", "val_end", "turnover"]


class EntryExitAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'stock', 'date_entry', 'chart_entry',
        'num_entry', 'price_entry', 'price_set_profit', 'price_loss_cut',
        'date_exit', 'num_exit', 'chart_exit', 'price_exit', 'reason_lose',
        'memo', 'commission',
    ]


admin.site.register(Stocks, StocksAdmin)
admin.site.register(HoldingStocks, HoldingStocksAdmin)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(StockDataByDate, StockDataByDateAdmin)
admin.site.register(EntryExit, EntryExitAdmin)