from django.contrib import admin
from .models import *
# Register your models here.


class KakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'way', 'tag', 'memo', 'usage', 'move_from', 'move_to']


class ResourcesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'initial_val', 'color']


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


admin.site.register(Kakeibos, KakeibosAdmin)
admin.site.register(Resources, ResourcesAdmin)
admin.site.register(Usages, UsagesAdmin)
admin.site.register(SharedKakeibos, SharedKakeibosAdmin)
admin.site.register(Cards, CardsAdmin)
admin.site.register(CreditItems, CreditItemsAdmin)
admin.site.register(Credits, CreditsAdmin)