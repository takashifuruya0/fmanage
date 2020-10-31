from django import forms
from django.conf import settings
from lancers.models import Category


class OpportunityForm(forms.Form):
    oppid = forms.CharField(label="直接依頼ID/提案ID", help_text="/work_offer/XXXXXX または //work/proposal/XXXXX")
    type_opp = forms.ChoiceField(
        label="商談種類", help_text="追加受注は選択不可",
        choices=settings.CHOICES_TYPE_OPPORTUNITY, widget=forms.Select()
    )
    category_id = forms.ModelChoiceField(Category.objects, label="カテゴリー")
    status = forms.ChoiceField(choices=settings.CHOICES_STATUS_OPPORTUNITY, label="ステータス")
    memo = forms.CharField(widget=forms.Textarea(), label="補足")