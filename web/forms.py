from django import forms
from web.models import Entry, Order, Stock, SBIAlert, EntryStatus, StockValueData
from datetime import date


class EntryForm(forms.ModelForm):
    """
    Memo モデルの作成、更新に使われる Django フォーム。
    ModelForm を継承して作れば、HTMLで表示したいフィールドを
    指定するだけで HTML フォームを作ってくれる。
    """
    is_plan = forms.BooleanField(initial=True, required=False, label="EntryPlan")

    class Meta:
        model = Entry
        fields = [
            "stock",
            "entry_type",
            "border_profit_determination",
            'border_loss_cut',
            "num_plan",
            "val_plan",
            'reason_win_loss',
            'memo',
            "is_plan",
            "status",
            "user",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        instance = kwargs.get("instance")
        if instance:
            if not instance.is_closed and not instance.is_plan:
                self.fields.pop("reason_win_loss")
                self.fields.pop("is_plan")
                self.fields['stock'].disabled = True
            if instance.entry_type:
                self.fields['status'].queryset = EntryStatus.objects.filter(entry_type=instance.entry_type)
                self.fields['entry_type'].disabled = True
        else:
            for d in ("reason_win_loss", "status",):
                self.fields.pop(d)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['entry'].queryset = self.get_entry()

    def get_entry(self):
        if self.initial:
            return Entry.objects.filter(stock=self.initial['stock'])
        else:
            return Entry.objects.filter(is_closed=False)


class InvestmentForm(forms.Form):
    value = forms.IntegerField(required=True)
    is_investment = forms.BooleanField(required=False, label="増資")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class OrderLinkForm(forms.Form):
    orders = forms.ModelMultipleChoiceField(
        queryset=Order.objects.all(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock
        fields = ["code",]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SBIAlertForm(forms.ModelForm):

    class Meta:
        model = SBIAlert
        fields = ["stock", "val", "type", ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class TrustOrderForm(forms.ModelForm):
    is_buy = forms.BooleanField(label="買い注文")
    is_nisa = forms.BooleanField(label="NISA")

    class Meta:
        model = Order
        exclude = ("is_simulated", "fkmanage_id", "chart")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['entry'].queryset = Entry.objects.filter(stock__is_trust=True)
        self.fields['stock'].queryset = Stock.objects.filter(is_trust=True)
        self.fields['datetime'].widget.attrs['readonly'] = 'readonly'

    def get_entry(self):
        if self.initial:
            return Entry.objects.filter(stock=self.initial['stock'])
        else:
            return Entry.objects.filter(stock__is_trust=True)
