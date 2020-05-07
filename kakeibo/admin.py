from django.contrib import admin
from .models import *
from dateutil.relativedelta import relativedelta
from django.contrib.admin.helpers import ActionForm
from django import forms
# Register your models here.


def activate(modeladmin, request, queryset):
    queryset.update(is_active=True)
    activate.short_description = "Mark selected stories as active"


class KakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'way', 'memo', 'usage', 'move_from', 'move_to', 'event', "is_active"]
    list_filter = ['date', 'usage__name', 'event', ]
    list_editable = ['event', "is_active", ]
    search_fields = ['memo', ]
    actions = [activate]


class ResourcesAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'date', 'current_val',
        'is_saving',  "is_active", "is_investment",
    ]
    list_editable = ['is_active', "is_saving", "is_investment"]
    actions = [activate]


class UsagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'is_expense', 'color', "is_active"]
    list_editable = ['is_active']
    actions = [activate]


class SharedKakeibosAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'fee', 'memo', 'usage', 'paid_by', 'is_settled', "is_active"]
    list_filter = ['date', 'usage__name']
    search_fields = ['memo']
    list_editable = ['is_active']
    actions = [activate]


class CreditsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'debit_date', 'fee', 'credit_item', 'kakeibo']


class CreditItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date', 'usage', 'color', ]


class CronKakeiboAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'usage', 'move_from', 'move_to', "is_active"]
    list_editable = ['is_active']
    actions = [activate]


class CronSharedAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'usage', 'move_from', 'paid_by', "is_active"]
    list_editable = ['is_active']
    actions = [activate]


class UsualRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'fee', 'way', 'memo', 'usage', 'move_from', 'move_to', "is_active"]
    list_editable = ['is_active']
    actions = [activate]


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'name', 'memo', "is_active"]


class BudgetAdmin(admin.ModelAdmin):
    list_display = ["id", "date", "takashi", "hoko", "total"]


class YearMonthForm(ActionForm):
    year = forms.IntegerField(label="年", initial=date.today().year)
    month = forms.IntegerField(label="月", initial=date.today().month)


class TargetAdmin(admin.ModelAdmin):
    list_display = ["id", "date", "val", "type", "memo"]
    list_editable = ["date", "val", "type", "memo"]
    list_filter = ["date", "type"]
    actions = ['copy_next_month', 'copy_next_year', ]

    # action_form = YearMonthForm

    def copy_next_year(self, request, queryset):
        for obj in queryset.order_by('date'):
            memo = obj.__str__()
            obj.pk = None
            obj.date = obj.date + relativedelta(years=1)
            obj.memo = "Copied from {}".format(memo)
            obj.save()

    def copy_next_month(self, request, queryset):
        for obj in queryset.order_by('date'):
            memo = obj.__str__()
            obj.pk = None
            obj.date = obj.date + relativedelta(months=1)
            obj.memo = "Copied from {}".format(memo)
            obj.save()

    copy_next_year.short_description = "翌年へコピー"
    copy_next_month.short_description = "翌月へコピー"


admin.site.register(Kakeibos, KakeibosAdmin)
admin.site.register(Resources, ResourcesAdmin)
admin.site.register(Usages, UsagesAdmin)
admin.site.register(SharedKakeibos, SharedKakeibosAdmin)
admin.site.register(CreditItems, CreditItemsAdmin)
admin.site.register(Credits, CreditsAdmin)
admin.site.register(CronKakeibo, CronKakeiboAdmin)
admin.site.register(CronShared, CronSharedAdmin)
admin.site.register(UsualRecord, UsualRecordAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(Target, TargetAdmin)