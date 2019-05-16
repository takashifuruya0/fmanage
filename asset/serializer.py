# coding: utf-8

from rest_framework import serializers

from .models import Stocks, Orders, AssetStatus, HoldingStocks


class StocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stocks
        fields = ("code", "name",)


class OrdersSerializer(serializers.ModelSerializer):
    stock = StocksSerializer()

    class Meta:
        model = Orders
        fields = (
            'datetime', 'order_type', 'stock', 'num', 'price',
            'commission', 'is_nisa', 'chart',
        )


class HoldingStocksSerializer(serializers.ModelSerializer):
    stock = StocksSerializer()

    class Meta:
        model = HoldingStocks
        fields = ('date', 'stock', 'num', 'price', )


class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = (
            'date', 'total', 'buying_power', 'investment',
            'stocks_value', 'other_value',
        )