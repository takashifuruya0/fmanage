from django.contrib import admin
from django.contrib import messages
from lancers.models import *
from django.utils.safestring import mark_safe
from datetime import date
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats import base_formats
from lancers.functions import mylib_lancers
from lancers.forms import OpportunityWorkForm
# Register your models here.


# ===========================
# Resource
# ===========================
class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        exclude = ("created_at", "created_by", "last_updated_at", "last_updated_by", )


class ClientResource(resources.ModelResource):
    class Meta:
        model = Client
        exclude = ("created_at", "created_by", "last_updated_at", "last_updated_by",)


class OpportunityResource(resources.ModelResource):
    class Meta:
        model = Opportunity
        exclude = ("created_at", "created_by", "last_updated_at", "last_updated_by",)


class OpportunityWorkResource(resources.ModelResource):
    class Meta:
        model = OpportunityWork
        exclude = ("created_at", "created_by", "last_updated_at", "last_updated_by",)


# ===========================
# Inline
# ===========================
class RelatedOpportunityInline(admin.TabularInline):
    model = Opportunity.related_opportunity.through
    fk_name = "from_opportunity"
    verbose_name = "関連案件"
    verbose_name_plural = "関連案件"
    # https://www.366service.com/jp/qa/3336ea0ab72de9e60ab3a72a5059ef96
    # def get_queryset(self, request):
    #     return Opportunity.objects.filter(type="追加受注")


class OpportunityInline(admin.TabularInline):
    model = Opportunity
    fields = (
        "val", "status", "type", "_get_val", "_get_working_time", "_get_unit_val",
    )
    readonly_fields = (
        "name", "val", "status", "type", "_get_val", "_get_working_time", "_get_unit_val",
    )
    min_num = 1
    show_change_link = True

    def _get_val(self, obj):
        return obj.get_val()
    _get_val.short_description = '報酬額合計（税込）'

    def _get_working_time(self, obj):
        return obj.get_working_time(is_hour=True)
    _get_working_time.short_description = '労働時間合計（時間）'

    def _get_unit_val(self, obj):
        return obj.get_unit_val()
    _get_unit_val.short_description = '単価（円/h）'


class OpportunityWorkInline(admin.TabularInline):
    model = OpportunityWork
    exclude = ("memo", )


class CategoryLevelInline(admin.TabularInline):
    model = CategoryLevel
    exclude = ("sync_id", )


# ===========================
# Admin
# ===========================
class ServiceAdmin(ImportExportModelAdmin):
    list_display = (
        "pk", "_get_service_name", "version", "val",
        "is_regular", "is_active", "date_deactivate", "_get_count"
    )
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    )
    resource_class = ServiceResource
    search_fields = ("name", )
    list_filter = ("is_active", )
    ordering = ("-is_active", "-is_regular", "-val")
    actions = ["_version_up", ]

    def _get_service_name(self, obj):
        if not obj.is_active:
            return "無効_{}".format(obj.name)
        return obj.name
    _get_service_name.short_description = "サービス名"

    def _get_count(self, obj):
        return obj.opportunity_set.filter(status__startswith="選定").count()
    _get_count.short_description = "提供数"

    def _version_up(self, request, queryset):
        for obj in queryset:
            if obj.is_active:
                obj.is_active = False
                obj.date_deactivate = date.today()
                obj.save()
                obj.pk = None
                obj.is_active = True
                obj.date_deactivate = None
                obj.version += 1
                obj.save()
        messages.success(request, "指定のサービスを更新しました")
    _version_up.short_description = "サービスを更新する"


class ClientAdmin(ImportExportModelAdmin):
    list_display = ("name", "client_id", "client_type", "name_slack", "_get_num_opportunities", "_has_profile")
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
        "_get_num_opportunities", "_get_client_url",
    )
    inlines = [OpportunityInline]
    resource_class = ClientResource
    search_fields = ("name", "client_id", "name_slack", "client_type")
    list_filter = ("client_type", "name_slack",)

    def _has_profile(self, obj):
        if obj.client_profile:
            return obj.client_profile.last_updated_at
        elif obj.client_type == "MENTA":
            return "要作成"
        else:
            return "対象外"
    _has_profile.short_description = "プロファイル"

    def _get_num_opportunities(self, obj):
        return obj.opportunity_set.count()
    _get_num_opportunities.short_description = '案件数'

    def _get_client_url(self, obj):
        if obj.client_type == "MENTA":
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://menta.work/user/{}>LINK</a>".format(
                    obj.client_id)
            )
        elif obj.client_type == "Lancers":
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://www.lancers.jp/client/{}>LINK</a>".format(
                    obj.client_id)
            )
        else:
            return None
    _get_client_url.short_description = "顧客URL"


class OpportunityAdmin(ImportExportModelAdmin):
    inlines = [
        OpportunityWorkInline,
        # RelatedOpportunityInline
    ]
    search_fields = ("name", "client__name", )
    filter_horizontal = ('sub_categories', 'related_opportunity',)
    list_display = (
        "pk", "date_open", "date_close",
        "name", "opportunity_id", "client", "category", "status", "type",
        # "_get_val", "_get_working_time", "_get_unit_val",
        # "_get_opportunity_url", "_get_proposal_url",
    )
    # list_display_links = ("client", )
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
        "_get_val", "_get_working_time", "_get_unit_val",
        "_get_opportunity_url", "_get_proposal_url",
    )
    list_filter = ("status", "type", "date_payment")
    if settings.ENVIRONMENT == "develop":
        actions = ["_action", "_sync"]
    resource_class = OpportunityResource
    autocomplete_fields = ("client", "category", "original_opportunity")

    def _get_val(self, obj):
        return obj.get_val()
    _get_val.short_description = '報酬額合計（税込）'

    def _get_working_time(self, obj):
        return obj.get_working_time(is_hour=True)
    _get_working_time.short_description = '労働時間合計（時間）'

    def _get_unit_val(self, obj):
        return obj.get_unit_val()
    _get_unit_val.short_description = '単価（円/h）'

    def _get_opportunity_url(self, obj):
        if obj.client.client_type == "MENTA":
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://menta.work/bosyu/{}>LINK</a>".format(
                    obj.opportunity_id)
            )
        elif obj.client.client_type == "Lancers":
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://www.lancers.jp/work/detail/{}>LINK</a>".format(obj.opportunity_id)
            )
        else:
            return None
    _get_opportunity_url.short_description = "案件URL"

    def _get_proposal_url(self, obj):
        if obj.client.is_nonlancers or not obj.proposal_id:
            return None
        else:
            return mark_safe(
                "<a target='_blank' rel='noopener noreferrer' href=https://www.lancers.jp/work/proposal/{}>LINK</a>".format(obj.proposal_id)
            )
    _get_proposal_url.short_description = "提案URL"

    def _action(self, request, queryset):
        idlist = list()
        for obj in queryset:
            res = mylib_lancers.update_opportunity2(obj)
            if not res:
                messages.warning(request, "Failed@{}".format(obj))
            else:
                idlist.append(obj.pk)
        messages.success(request, "Updated @{}".format(idlist))
    _action.short_description = "商談を更新する（Selenium）"

    def _sync(self, request, queryset):
        messages.success(request, "")
        messages.warning(request, "")
        for obj in queryset:
            r = mylib_lancers.sync(obj, request.user)
            if r:
                messages.add_message(request, messages.SUCCESS, "{}は同期されました！".format(obj))
            else:
                messages.add_message(request, messages.WARNING, "{}は同期されませんでした".format(obj))
    _sync.short_description = "商談を同期する（Dev→Prod）"

    fieldsets = (
        ("システム情報", {
            "fields": (
                ("created_at", "created_by"),
                ("last_updated_at", "last_updated_by"),
                "sync_id",
            )
        }),
        ("基本情報", {
            "fields": (
                "name",
                ("opportunity_id", "_get_opportunity_url",),
                ("direct_opportunity_id", ),
                "date_open", "date_close", "date_payment",
                "related_opportunity",
                "status",
                ("type", "is_regular", "is_copied_to"),
                "original_opportunity",
                "category", "sub_categories",
                "service",
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


class OpportunityWorkAdmin(ImportExportModelAdmin):
    list_display = (
        "pk", "opportunity", "datetime_start", "datetime_end", "get_working_time", "is_in_calendar"
    )
    readonly_fields = ("working_time", "created_by", "created_at", "last_updated_by", "last_updated_at", )
    resource_class = OpportunityWorkResource
    autocomplete_fields = ("opportunity", )
    form = OpportunityWorkForm
    search_fields = ("opportunity__name", )
    list_filter = ("opportunity__status", )
    # list_display_links = ("opportunity", )


class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    search_fields = ("name", )
    readonly_fields = (
        "created_by", "created_at", "last_updated_by", "last_updated_at",
    )


# ===========================
# Register
# ===========================
admin.site.register(Client, ClientAdmin)
admin.site.register(Opportunity, OpportunityAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(OpportunityWork, OpportunityWorkAdmin)
admin.site.register(Service, ServiceAdmin)