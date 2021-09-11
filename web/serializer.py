# coding: utf-8
from rest_framework import serializers
from web.models import Stock, Order, AssetStatus, AssetTarget, Entry, StockValueData
from web.models import ReasonWinLoss, EntryStatus, Ipo, Dividend


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class SimpleStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ("code", "name")



class OrderSerializer(serializers.ModelSerializer):
    stock = SimpleStockSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class AssetTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTarget
        fields = '__all__'


class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = '__all__'


class StockValueDataSerializer(serializers.ModelSerializer):
    stock = SimpleStockSerializer()

    class Meta:
        model = StockValueData
        fields = '__all__'


class ReasonWinLossSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonWinLoss
        fields = ("reason", "is_win")


class EntryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryStatus
        fields = ("status", )


class EntrySerializer(serializers.ModelSerializer):
    stock = SimpleStockSerializer()
    reason_win_loss = ReasonWinLossSerializer()
    status = EntryStatusSerializer()
    orders = serializers.SerializerMethodField()

    class Meta:
        model = Entry
        fields = '__all__'

    def get_orders(self, instance):
        orders = Order.objects.filter(entry=instance)
        res = [
            {
                "pk": o.pk,
                "datetime": o.datetime,
                "is_buy": o.is_buy,
                "val": o.val,
                "num": o.num,
                "is_nisa": o.is_nisa,
                "commission": o.commission,
            }
            for o in orders
        ]
        return res
            



class DividendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dividend
        fields = "__all__"


class IpoSerializer(serializers.ModelSerializer):
    stock = SimpleStockSerializer()
    class Meta:
        model = Ipo
        fields = "__all__"