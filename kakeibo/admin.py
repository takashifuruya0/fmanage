from django.contrib import admin
from .models import *
from asset.models import *
# Register your models here.


class KakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'way', 'tag', 'memo', 'usage', 'move_from', 'move_to', 'event']
    list_filter = ['date', 'usage__name']
    search_fields = ['memo']


class ResourcesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'initial_val', 'current_val', 'is_saving', 'color']


class UsagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'is_expense', 'color']


class SharedKakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'memo', 'usage', 'paid_by', 'is_settled']
    list_filter = ['date', 'usage__name']
    search_fields = ['memo']


class CreditsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'debit_date', 'fee', 'credit_item', 'kakeibo']


class CreditItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'usage', 'color', ]


class CronKakeiboAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'usage', 'move_from', 'move_to']


class CronSharedAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'usage', 'move_from', 'paid_by']


class UsualRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'memo', 'usage', 'move_from', 'move_to']


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'name', 'memo', ]


admin.site.register(Kakeibos, KakeibosAdmin)
admin.site.register(Resources, ResourcesAdmin)
admin.site.register(Usages, UsagesAdmin)
admin.site.register(SharedKakeibos, SharedKakeibosAdmin)
# admin.site.register(Cards, CardsAdmin)
admin.site.register(CreditItems, CreditItemsAdmin)
admin.site.register(Credits, CreditsAdmin)
# admin.site.register(Colors, ColorsAdmin)
# admin.site.register(Stocks, StocksAdmin)
# admin.site.register(HoldingStocks, HoldingStocksAdmin)
# admin.site.register(AssetStatus, AssetStatusAdmin)
# admin.site.register(Orders, OrdersAdmin)
# admin.site.register(StockDataByDate, StockDataByDateAdmin)
admin.site.register(CronKakeibo, CronKakeiboAdmin)
admin.site.register(CronShared, CronSharedAdmin)
admin.site.register(UsualRecord, UsualRecordAdmin)
admin.site.register(Event, EventAdmin)