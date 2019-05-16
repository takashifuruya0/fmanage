# coding: utf-8

from rest_framework import serializers

from .models import *


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
