from django.contrib import admin
from .models import *
from asset.models import *
# Register your models here.


class KakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'way', 'tag', 'memo', 'usage', 'move_from', 'move_to']


class ResourcesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'initial_val', 'current_val', 'is_saving', 'color']


class UsagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'is_expense', 'color']


class SharedKakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'memo', 'usage', 'paid_by', 'is_settled']


class CardsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'color']


class CreditsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'debit_date', 'fee', 'credit_item', 'card']


class CreditItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'usage', 'color']


class ColorsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class StocksAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']


class HoldingStocksAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', "get_holding_time", 'stock', 'num', 'price', 'get_current_price']


class AssetStatusAdmin(admin.ModelAdmin):
    list_display = ["date", "total", "buying_power", "stocks_value", "other_value", "investment", "get_total"]


class OrdersAdmin(admin.ModelAdmin):
    list_display = ["datetime", "order_type", "stock", "num", "price", "commission", "is_nisa"]


class StockDataByDateAdmin(admin.ModelAdmin):
    list_display = ["stock", "date", "val_start", "val_high", "val_low", "val_end", "turnover"]


class CronKakeiboAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'usage', 'move_from', 'move_to']

admin.site.register(Kakeibos, KakeibosAdmin)
admin.site.register(Resources, ResourcesAdmin)
admin.site.register(Usages, UsagesAdmin)
admin.site.register(SharedKakeibos, SharedKakeibosAdmin)
admin.site.register(Cards, CardsAdmin)
admin.site.register(CreditItems, CreditItemsAdmin)
admin.site.register(Credits, CreditsAdmin)
admin.site.register(Colors, ColorsAdmin)
admin.site.register(Stocks, StocksAdmin)
admin.site.register(HoldingStocks, HoldingStocksAdmin)
admin.site.register(AssetStatus, AssetStatusAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(StockDataByDate, StockDataByDateAdmin)
admin.site.register(CronKakeibo, CronKakeiboAdmin)
