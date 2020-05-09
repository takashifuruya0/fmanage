from django import forms

from kakeibo.models import Kakeibos, SharedKakeibos, Credits, CreditItems, Usages, Event


class KakeiboForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """
    choices = ((c, c) for c in ["支出（現金）", "支出（クレジット）", "支出（Suica）", "引き落とし", "収入", "振替", "その他"])
    way = forms.TypedChoiceField(choices=choices)
    way.widget.attrs['onchange'] = 'fill_resource()'
    tag_copy_to_shared = forms.BooleanField(required=False, label="共通へコピー")
    usage = forms.ModelChoiceField(
        queryset=Usages.objects.filter(is_active=True).order_by('is_expense', "pk"),
        required=False
    )

    class Meta:
        model = Kakeibos
        fields = [
            'date', 'fee', 'way', 'usage', 'move_from', 'move_to', 'memo',
            'event', "tag_copy_to_shared",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['readonly'] = 'readonly'


class SharedKakeiboForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """
    choices_paid_by = ((c, c) for c in ["敬士", "朋子",])
    paid_by = forms.TypedChoiceField(choices=choices_paid_by)
    date = forms.DateField()
    usage = forms.ModelChoiceField(
        queryset=Usages.objects.filter(is_expense=True, is_active=True)
    )

    class Meta:
        model = SharedKakeibos
        fields = ['date', 'fee', 'usage', 'paid_by', 'memo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['readonly'] = 'readonly'


class CreditForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """

    class Meta:
        model = Credits
        fields = ['date', 'debit_date', 'fee', 'credit_item', "memo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CreditItemForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """

    class Meta:
        model = CreditItems
        fields = ['name', 'usage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UsageForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """

    class Meta:
        model = Usages
        fields = ['name', 'is_expense', 'memo', 'date', 'is_active', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class EventForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """

    class Meta:
        model = Event
        fields = ['date', 'name', 'memo', 'detail', 'date', 'sum_plan', 'is_active', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
