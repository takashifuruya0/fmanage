from django.contrib import admin
from lancers.models import *
from django.utils.safestring import mark_safe
# Register your models here.


class OpportunityInline(admin.TabularInline):
    model = Opportunity
    fields = (
        "val", "status", "type", "_get_val", "_get_working_time", "_get_unit_val",
    )
    readonly_fields = (
        "name", "val", "status", "type", "_get_val", "_get_working_time", "_get_unit_val",
    )
    min_num = 1

    def _get_val(self, obj):
        return obj.get_val()
    _get_val.short_description = '報酬額合計（税込）'

    def _get_working_time(self, obj):
        return obj.get_working_time()
    _get_working_time.short_description = '労働時間合計（分）'

    def _get_unit_val(self, obj):
        return obj.get_unit_val()
    _get_unit_val.short_description = '単価（円/h）'


class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "client_id", "is_nonlancers", "_get_num_opportunities", )
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
        "_get_num_opportunities",
    )
    inlines = [OpportunityInline]

    def _get_num_opportunities(self, obj):
        return obj.opportunity_set.count()
    _get_num_opportunities.short_description = '案件数'


class OpportunityWorkInline(admin.TabularInline):
    model = OpportunityWork
    exclude = ("memo", )


class OpportunityAdmin(admin.ModelAdmin):
    inlines = [OpportunityWorkInline]
    list_display = (
        "name", "opportunity_id", "client", "category", "status", "type",
        "_get_val", "_get_working_time", "_get_unit_val",
        "_get_opportunity_url", "_get_proposal_url",
    )
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
        "_get_val", "_get_working_time", "_get_unit_val",
        "_get_opportunity_url", "_get_proposal_url",
    )
    list_filter = ("status", "category", )

    def _get_val(self, obj):
        return obj.get_val()
    _get_val.short_description = '報酬額合計（税込）'

    def _get_working_time(self, obj):
        return obj.get_working_time()
    _get_working_time.short_description = '労働時間合計（分）'

    def _get_unit_val(self, obj):
        return obj.get_unit_val()
    _get_unit_val.short_description = '単価（円/h）'

    def _get_opportunity_url(self, obj):
        if obj.client.is_nonlancers:
            return None
        else:
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://www.lancers.jp/work/detail/{}>LINK</a>".format(obj.opportunity_id)
            )
    _get_opportunity_url.short_description = "案件URL"

    def _get_proposal_url(self, obj):
        if obj.client.is_nonlancers or not obj.proposal_id:
            return None
        else:
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://www.lancers.jp/work/proposal/{}>LINK</a>".format(obj.proposal_id)
            )
    _get_proposal_url.short_description = "提案URL"

    fieldsets = (
        ("システム情報", {
            "fields": (
                ("created_at", "created_by"),
                ("last_updated_at", "last_updated_by"),
            )
        }),
        ("基本情報", {
            "fields": (
                "name", ("opportunity_id", "_get_opportunity_url",),
                ("direct_opportunity_id", ),
                "related_opportunity",
                "status", "type",
                ("category", "sub_categories"),
            )
        }),
        ("依頼情報", {
            "fields": (
                "client", "val", "val_payment", "budget",
                "description_opportunity", "detail_opportunity",
                "datetime_open_opportunity",  "datetime_close_opportunity",
                "datetime_updated_opportunity", "date_desired_delivery",
            ),
        }),
        ("検討情報", {
            "fields": (
                "drive_url", "knowledge_url",
                "memo",
            )
        }),
        ("提案情報", {
            "fields": (
                ("proposal_id", "_get_proposal_url"),
                "date_proposal", "description_proposal",
                "date_proposed_delivery", "num_proposal"
            )
        }),
        ("INFO", {
           "fields": (
               "_get_val", "_get_working_time", "_get_unit_val"
           )
        }),
    )


class OpportunityWorkAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "is_in_calendar", "get_working_time")
    readonly_fields = ("created_by", "created_at", "last_updated_by", "last_updated_at")


admin.site.register(Client, ClientAdmin)
admin.site.register(Opportunity, OpportunityAdmin)
admin.site.register(Category)
admin.site.register(OpportunityWork, OpportunityWorkAdmin)