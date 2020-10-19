from django.contrib import admin
from lancers.models import *
# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "client_id", "is_nonlancers")
    readonly_fields = ("created_by", "created_at", "last_updated_by", "last_updated_at")


class OpportunityAdmin(admin.ModelAdmin):
    list_display = (
        "name", "opportunity_id", "client", "category", "status", "type",
        "_get_val", "_get_working_time", "_get_unit_val"
    )
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
        "_get_val", "_get_working_time", "_get_unit_val"
    )

    def _get_val(self, obj):
        return obj.get_val()
    _get_val.short_description = '報酬額合計（税込）'

    def _get_working_time(self, obj):
        return obj.get_working_time()
    _get_working_time.short_description = '労働時間合計（分）'

    def _get_unit_val(self, obj):
        return obj.get_unit_val()
    _get_unit_val.short_description = '単価（円/h）'


class OpportunityWorkAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "is_in_calendar", "get_working_time")
    readonly_fields = ("created_by", "created_at", "last_updated_by", "last_updated_at")


admin.site.register(Client, ClientAdmin)
admin.site.register(Opportunity, OpportunityAdmin)
admin.site.register(Category)
admin.site.register(OpportunityWork, OpportunityWorkAdmin)