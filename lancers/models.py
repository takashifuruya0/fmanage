from django.db import models
from django.db.models import Sum
from django_currentuser.middleware import get_current_authenticated_user
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.conf import settings
# Create your models here.


class BaseModel(models.Model):
    objects = None
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    last_updated_at = models.DateTimeField(auto_now=True, verbose_name="最終更新日時")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_created_by",
        verbose_name="作成者", editable=False
    )
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_last_updated_by",
        verbose_name="最終更新者", editable=False
    )
    is_active = models.BooleanField(default=True, verbose_name="有効")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = get_current_authenticated_user()
        self.last_updated_by = get_current_authenticated_user()
        super(BaseModel, self).save(*args, **kwargs)

    def save_from_shell(self, user):
        if not self.pk:
            self.created_by = user
        self.last_updated_by = user
        super(BaseModel, self).save()


class Category(BaseModel):
    objects = None
    name = models.CharField(max_length=255, verbose_name="カテゴリー名")
    memo = models.TextField(verbose_name="メモ", null=True, blank=True)

    class Meta:
        verbose_name = "カテゴリー"
        verbose_name_plural = "カテゴリー"

    def __str__(self):
        return self.name


class Client(BaseModel):
    objects = None
    name = models.CharField(max_length=255, verbose_name="クライアント名")
    client_id = models.CharField(max_length=255, verbose_name="クライアントID")
    is_nonlancers = models.BooleanField(default=False, verbose_name="ランサーズ以外")

    class Meta:
        verbose_name = "クライアント"
        verbose_name_plural = "クライアント"

    def __str__(self):
        return "【{}】{}".format(self.client_id, self.name)


class Opportunity(BaseModel):
    """FIELDS"""
    objects = None
    # 共通
    name = models.CharField(max_length=255, verbose_name="案件名")
    opportunity_id = models.CharField(max_length=255, verbose_name="案件ID", null=True, blank=True)
    direct_opportunity_id = models.CharField(max_length=255, verbose_name="直接依頼ID", null=True, blank=True)
    related_opportunity = models.ManyToManyField(
        "self", verbose_name="関連案件", blank=True,
        limit_choices_to={
            "is_active": True,
        }
    )
    date_open = models.DateField(verbose_name="案件開始日", blank=True, null=True)
    date_close = models.DateField(verbose_name="案件終了日", blank=True, null=True)
    client = models.ForeignKey(Client, verbose_name="クライアント", on_delete=models.CASCADE)
    status = models.CharField(max_length=255, verbose_name="ステータス", choices=settings.CHOICES_STATUS_OPPORTUNITY)
    type = models.CharField(max_length=255, verbose_name="タイプ", choices=settings.CHOICES_TYPE_OPPORTUNITY)
    category = models.ForeignKey(
        Category, verbose_name="カテゴリー", on_delete=models.CASCADE, null=True, blank=True
    )
    sub_categories = models.ManyToManyField(
        Category, verbose_name="サブカテゴリー", blank=True, related_name="sub_categories"
    )
    # 依頼
    val_payment = models.IntegerField(verbose_name="クライアント支払額（税込）", null=True, blank=True)
    val = models.IntegerField(verbose_name="報酬額（税込）")
    description_opportunity = models.TextField(verbose_name="依頼内容", null=True, blank=True)
    detail_opportunity = JSONField(verbose_name="依頼詳細（JSON）", null=True, blank=True)
    budget = models.CharField(max_length=255, verbose_name="予算", null=True, blank=True)
    datetime_open_opportunity = models.DateTimeField(verbose_name="依頼開始日時", null=True, blank=True)
    datetime_close_opportunity = models.DateTimeField(verbose_name="依頼締切日時", null=True, blank=True)
    date_desired_delivery = models.DateField(verbose_name="希望納期", null=True, blank=True)
    datetime_updated_opportunity = models.DateTimeField(verbose_name="依頼更新日時", null=True, blank=True)
    # 提案
    proposal_id = models.CharField(max_length=255, verbose_name="提案ID", null=True, blank=True)
    date_proposal = models.DateField(verbose_name="提案日", null=True, blank=True)
    description_proposal = models.TextField(verbose_name="提案内容", null=True, blank=True)
    date_proposed_delivery = models.DateField(verbose_name="提案納期", null=True, blank=True)
    num_proposal = models.IntegerField(verbose_name="提案件数", null=True, blank=True)
    # 検討
    memo = models.TextField(verbose_name="メモ", null=True, blank=True)
    drive_url = models.URLField(verbose_name="GoogleDrive", null=True, blank=True)
    knowledge_url = models.URLField(verbose_name="Knowledge", null=True, blank=True)

    """META"""
    class Meta:
        verbose_name = "案件"
        verbose_name_plural = "案件"

    def __str__(self):
        return "【{}】{}".format(self.opportunity_id, self.name)

    def get_working_time(self, is_hour=False):
        works = self.opportunitywork_set.all()
        ros = self.related_opportunity.all()
        if works.count() == 0 or self.type == "追加受注":
            sum_work = 0
        elif ros.count() > 0:
            sum_work = sum([ro.get_working_time() for ro in ros]) + sum([work.get_working_time() for work in works])
        else:
            sum_work = sum([work.get_working_time() for work in works])
        return sum_work/60 if is_hour else sum_work

    def get_unit_val(self):
        working_time = self.get_working_time()
        if working_time == 0:
            return None
        else:
            return int(self.get_val()/working_time*60)

    def get_val(self):
        ros = self.related_opportunity.all()
        if self.type == "追加受注":
            return None
        elif ros:
            return ros.aggregate(v=Sum('val'))['v'] + self.val
        else:
            return self.val


class OpportunityWork(BaseModel):
    CHOICES_TYPE_WORK = (
        (k, k) for k in ("提案整理", "作業", )
    )
    objects = None
    opportunity = models.ForeignKey(
        Opportunity, verbose_name="案件", on_delete=models.CASCADE,
        limit_choices_to={
            "type__in": ("直接受注", "提案受注"),
            "status__in": ("相談中", "提案中", "選定/作業中", ),
        }
    )
    datetime_start = models.DateTimeField(verbose_name="開始時間", null=True, blank=True)
    datetime_end = models.DateTimeField(verbose_name="終了時間", null=True, blank=True)
    working_time = models.IntegerField(verbose_name="労働時間（分）", null=True, blank=True)
    is_in_calendar = models.BooleanField(verbose_name="カレンダーへ追加", default=False)
    memo = models.TextField(verbose_name="メモ", null=True, blank=True)

    class Meta:
        verbose_name = "案件活動"
        verbose_name_plural = "案件活動"

    def __str__(self):
        pk_zfill = str(self.pk).zfill(4)
        return "OW{}_{}".format(pk_zfill, self.opportunity)

    def get_working_time(self, is_hour=False):
        if is_hour:
            return self.working_time / 60
        else:
            return self.working_time

    def save(self, *args, **kwargs):
        if self.working_time:
            super(OpportunityWork, self).save()
        elif self.datetime_start and self.datetime_end:
            self.working_time = int((self.datetime_end-self.datetime_start).seconds/60)
            super(OpportunityWork, self).save()
        else:
            raise Exception('労働時間の登録が必要です')