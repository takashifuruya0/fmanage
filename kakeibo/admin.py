from django.contrib import admin
from .models import *
from asset.models import *
# Register your models here.


class KakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'way', 'tag', 'memo', 'usage', 'move_from', 'move_to']


class ResourcesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'initial_val', 'current_val', 'color']


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
    list_display = ['id', 'date', 'stock', 'num', 'average_price']


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
