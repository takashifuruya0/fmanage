from django import forms
from asset.models import Orders, Stocks


class OrdersForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """
    choices = ((c, c) for c in ["現物買", "現物売",])
    order_type = forms.TypedChoiceField(choices=choices)

    class Meta:
        model = Orders
        fields = ['datetime', 'order_type', 'stock', 'num', 'price', 'commission', 'is_nisa']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class StocksForm(forms.ModelForm):
    class Meta:
        model = Stocks
        fields = ['code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class AddInvestmentForm(forms.Form):
    value = forms.IntegerField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control',
               'placeholder': "追加投資額",
               }
    ))
    is_investment = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={
            'class': 'form-control',
        }
    ))
