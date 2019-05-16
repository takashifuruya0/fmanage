# coding:utf-8

import logging
logger = logging.getLogger("django")
from kakeibo.models import Usages, Resources, Kakeibos, SharedKakeibos
# django-rest-framework
from django_filters import rest_framework as dfilters
from rest_framework import viewsets
from kakeibo.serializer import UsagesSerializer, ResourcesSerializer, KakeibosSerializer, SharedKakeibosSerializer


# django-rest-framework
# class OrdersFilter(dfilters.FilterSet):
#     choices = (("現物売", "現物売",), ("現物買", "現物買"))
#     order_type = dfilters.ChoiceFilter(choices=choices)
#     stock = dfilters.ModelChoiceFilter(queryset=Stocks.objects.all())
#
#     class Meta:
#         fields = ("stock", "order_type")
#         model = Orders


class UsagesViewSet(viewsets.ModelViewSet):
    queryset = Usages.objects.all()
    serializer_class = UsagesSerializer
    # filter_class = OrdersFilter


class ResourcesViewSet(viewsets.ModelViewSet):
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer


class KakeibosViewSet(viewsets.ModelViewSet):
    queryset = Kakeibos.objects.all()
    serializer_class = KakeibosSerializer


class SharedKakeibosViewSet(viewsets.ModelViewSet):
    queryset = SharedKakeibos.objects.all()
    serializer_class = SharedKakeibosSerializer
