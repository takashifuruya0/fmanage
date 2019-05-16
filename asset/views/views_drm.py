# coding:utf-8

import logging
logger = logging.getLogger("django")
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders
# django-rest-framework
from django_filters import rest_framework as dfilters
from rest_framework import viewsets
from asset.serializer import OrdersSerializer, StocksSerializer, HoldingStocksSerializer, AssetStatusSerializer


# django-rest-framework
class OrdersFilter(dfilters.FilterSet):
    choices = (("現物売", "現物売",), ("現物買", "現物買"))
    order_type = dfilters.ChoiceFilter(choices=choices)
    stock = dfilters.ModelChoiceFilter(queryset=Stocks.objects.all())

    class Meta:
        fields = ("stock", "order_type")
        model = Orders


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    filter_class = OrdersFilter


class StocksViewSet(viewsets.ModelViewSet):
    queryset = Stocks.objects.all()
    serializer_class = StocksSerializer


class HoldingStocksViewSet(viewsets.ModelViewSet):
    queryset = HoldingStocks.objects.all()
    serializer_class = HoldingStocksSerializer


class AssetStatusViewSet(viewsets.ModelViewSet):
    queryset = AssetStatus.objects.all()
    serializer_class = AssetStatusSerializer
