from django import forms

from kakeibo.models import Kakeibos, SharedKakeibos, Credits, CreditItems


class KakeiboForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """
    choices = ((c, c) for c in ["支出（現金）", "支出（クレジット）", "引き落とし", "共通支出", "収入", "振替"])
    way = forms.TypedChoiceField(choices=choices)
    way.widget.attrs['onchange'] = 'fill_resource()'

    class Meta:
        model = Kakeibos
        fields = ['date', 'fee', 'usage', 'way', 'move_from', 'move_to', 'memo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SharedKakeiboForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """
    choices_paid_by = ((c, c) for c in ["敬士", "朋子",])
    paid_by = forms.TypedChoiceField(choices=choices_paid_by)
    date = forms.DateField()

    class Meta:
        model = SharedKakeibos
        fields = ['date', 'fee', 'usage', 'paid_by', 'memo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


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
