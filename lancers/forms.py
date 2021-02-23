from django import forms
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from lancers.models import Category, Opportunity, OpportunityWork, Service


class OpportunityForm(forms.Form):
    oppid = forms.CharField(label="直接依頼ID/提案ID", help_text="/work_offer/XXXXXX または //work/proposal/XXXXX")
    type_opp = forms.ChoiceField(
        label="商談種類", help_text="追加受注は選択不可",
        choices=Opportunity.CHOICES_TYPE_OPPORTUNITY, widget=forms.Select()
    )
    category_id = forms.ModelChoiceField(Category.objects, label="カテゴリー")
    status = forms.ChoiceField(choices=Opportunity.CHOICES_STATUS_OPPORTUNITY, label="ステータス")
    memo = forms.CharField(widget=forms.Textarea(), label="補足")


class OpportunityWorkForm(forms.ModelForm):
    opportunity = forms.ModelChoiceField(
        queryset=Opportunity.objects.filter(status__in=("相談中", "提案中", "選定/作業中", )),
        help_text="PPLのみ表示",
    )

    class Meta:
        model = OpportunityWork
        fields = ("opportunity", "datetime_start", "datetime_end", "memo", "is_in_calendar",)


class MentaForm(forms.Form):
    # CHOICES
    CHOICES_STATUS = (
        ("提案中", "提案中"), ("相談中", "相談中"), ("選定/作業中", "選定/作業中"),
    )
    # 共通
    client_name = forms.CharField(label="顧客名", required=True)
    client_id = forms.CharField(label="顧客ID", help_text="顧客URLのID")
    opportunity_id = forms.CharField(label="商談ID", help_text="依頼URLのID")
    date_open = forms.DateField(label="開始日", initial=date.today(), required=True)
    date_close = forms.DateField(label="終了日", initial=date.today()+relativedelta(months=1), required=True)
    # val = forms.IntegerField(label="収入（円）", min_value=0, required=True)
    # val_payment = forms.IntegerField(label="報酬（円）", min_value=0, required=True)
    status = forms.ChoiceField(label="ステータス", choices=CHOICES_STATUS, required=True)
    category = forms.ModelChoiceField(Category.objects, label="カテゴリー", required=True)
    sub_categories = forms.ModelMultipleChoiceField(Category.objects, label="サブカテゴリー", required=False)
    description_opportunity = forms.CharField(widget=forms.Textarea(), label="依頼")
    service = forms.ModelChoiceField(Service.objects.filter(is_active=True), label="サービス")
    # 提案
    date_proposal = forms.DateField(label="提案日", initial=date.today(), required=False)
    description_proposal = forms.CharField(widget=forms.Textarea(), label="提案", required=False)
    num_proposal = forms.IntegerField(label="提案数", widget=forms.NumberInput(), min_value=0, required=False)

