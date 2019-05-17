# coding:utf-8

import logging
logger = logging.getLogger("django")
from kakeibo.models import Usages, Resources, Kakeibos, SharedKakeibos, CreditItems, Credits
from kakeibo.models import CronKakeibo, CronShared, UsualRecord
# django-rest-framework
from django_filters import rest_framework as dfilters
from rest_framework import viewsets
from kakeibo.serializer import UsagesSerializer, ResourcesSerializer, KakeibosSerializer
from kakeibo.serializer import SharedKakeibosSerializer, CreditItemsSerializer, CreditsSerializer
from kakeibo.serializer import CronKakeiboSerializer, CronSharedSerializer, UsualRecordSerializer


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


class CreditItemsViewSet(viewsets.ModelViewSet):
    queryset = CreditItems.objects.all()
    serializer_class = CreditItemsSerializer


class CreditsViewSet(viewsets.ModelViewSet):
    queryset = Credits.objects.all()
    serializer_class = CreditsSerializer


class CronKakeiboViewSet(viewsets.ModelViewSet):
    queryset = CronKakeibo.objects.all()
    serializer_class = CronKakeiboSerializer


class CronSharedViewSet(viewsets.ModelViewSet):
    queryset = CronShared.objects.all()
    serializer_class = CronSharedSerializer


class UsualRecordViewSet(viewsets.ModelViewSet):
    queryset = UsualRecord.objects.all()
    serializer_class = UsualRecordSerializer

