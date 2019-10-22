# coding: utf-8

from rest_framework import serializers

from .models import Stocks, Orders, AssetStatus, HoldingStocks, StockDataByDate


class StocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stocks
        fields = ('pk', "code", "name", "industry", "market")


class OrdersSerializer(serializers.ModelSerializer):
    stock = StocksSerializer()

    class Meta:
        model = Orders
        fields = (
            'pk', 'datetime', 'order_type', 'stock', 'num', 'price',
            'commission', 'is_nisa', 'chart',
        )


class HoldingStocksSerializer(serializers.ModelSerializer):
    stock = StocksSerializer()

    class Meta:
        model = HoldingStocks
        fields = ('pk', 'date', 'stock', 'num', 'price', )


class AssetStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetStatus
        fields = (
            'pk', 'date', 'total', 'buying_power', 'investment',
            'stocks_value', 'other_value',
        )


class StockDataByDateSerializer(serializers.ModelSerializer):
    stock = StocksSerializer()

    class Meta:
        model = StockDataByDate
        fields = ('pk', 'stock', 'date', 'val_start', 'val_end', 'val_high', 'val_low', 'turnover')
