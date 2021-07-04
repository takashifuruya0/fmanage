# coding:utf-8

import logging
logger = logging.getLogger("django")
from kakeibo.models import Usages, Resources, Kakeibos, SharedKakeibos, CreditItems, Credits, Event
from kakeibo.models import CronKakeibo, CronShared, UsualRecord
# django-rest-framework
from django_filters import rest_framework as dfilters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from kakeibo.serializer import UsagesSerializer, ResourcesSerializer, KakeibosSerializer
from kakeibo.serializer import SharedKakeibosSerializer, CreditItemsSerializer, CreditsSerializer
from kakeibo.serializer import CronKakeiboSerializer, CronSharedSerializer, UsualRecordSerializer
from kakeibo.serializer import EventSerializer


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Usages.objects.all()
    serializer_class = UsagesSerializer
    # filter_class = OrdersFilter


class ResourcesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Resources.objects.all()
    serializer_class = ResourcesSerializer


class KakeibosViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Kakeibos.objects.all()
    serializer_class = KakeibosSerializer


class SharedKakeibosViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = SharedKakeibos.objects.all()
    serializer_class = SharedKakeibosSerializer


class CreditItemsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CreditItems.objects.all()
    serializer_class = CreditItemsSerializer


class CreditsViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Credits.objects.all()
    serializer_class = CreditsSerializer


class CronKakeiboViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CronKakeibo.objects.all()
    serializer_class = CronKakeiboSerializer


class CronSharedViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CronShared.objects.all()
    serializer_class = CronSharedSerializer


class UsualRecordViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = UsualRecord.objects.all()
    serializer_class = UsualRecordSerializer


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, )
    queryset = Event.objects.all()
    serializer_class = EventSerializer