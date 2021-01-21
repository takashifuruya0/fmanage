from django import forms
from django.conf import settings
from lancers.models import Category, Opportunity, OpportunityWork


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
