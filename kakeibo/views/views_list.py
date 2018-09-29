# coding:utf-8
from django.conf import settings
from django.views.generic import ListView
from pure_pagination.mixins import PaginationMixin
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos, Usages, Resources, Credits, CreditItems
# module
from kakeibo.functions.mylib import time_measure


# Create your views here.
class KakeiboList(PaginationMixin, ListView):
    model = Kakeibos
    ordering = ['-date']
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['usages'] = Usages.objects.all()
        res['resources'] = Resources.objects.all()
        res['ways'] = ["支出（現金）", "支出（クレジット）", "引き落とし", "共通支出", "収入"]
        return res

    def get_queryset(self):
        queryset = Kakeibos.objects.exclude(way="振替").order_by('-date')  # Default: Model.objects.all()
        if "usage" in self.request.GET:
            queryset = queryset.filter(usage=Usages.objects.get(pk=self.request.GET['usage']))
        if "year" in self.request.GET:
            queryset = queryset.filter(date__year=self.request.GET['year'])
        if "month" in self.request.GET:
            queryset = queryset.filter(date__month=self.request.GET['month'])
        if "way" in self.request.GET:
            queryset = queryset.filter(way=self.request.GET['way'])
        if "move_from" in self.request.GET:
            queryset = queryset.filter(move_from=self.request.GET['move_from'])
        if "move_to" in self.request.GET:
            queryset = queryset.filter(move_to=self.request.GET['move_to'])
        return queryset


class SharedList(PaginationMixin, ListView):
    model = SharedKakeibos
    ordering = ['-date']
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['paid_by'] = ["敬士", "朋子"]
        res['usages'] = list()
        for u in Usages.objects.all():
            if SharedKakeibos.objects.filter(usage=u).__len__() > 0:
                res['usages'].append(u)
        return res

    def get_queryset(self):
        queryset = SharedKakeibos.objects.all().order_by('-date')  # Default: Model.objects.all()
        if "usage" in self.request.GET:
            queryset = queryset.filter(usage=Usages.objects.get(pk=self.request.GET['usage']))
        if "year" in self.request.GET:
            queryset = queryset.filter(date__year=self.request.GET['year'])
        if "month" in self.request.GET:
            queryset = queryset.filter(date__month=self.request.GET['month'])
        if "paid_by" in self.request.GET:
            queryset = queryset.filter(paid_by=self.request.GET['paid_by'])
        return queryset


class CreditList(PaginationMixin, ListView):
    model = Credits
    ordering = ['-date']
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['credit_items'] = [ci for ci in CreditItems.objects.all()]
        res['usages'] = list()
        for u in Usages.objects.all():
            if CreditItems.objects.filter(usage=u).__len__() > 0:
                res['usages'].append(u)
        return res

    def get_queryset(self):
        queryset = Credits.objects.all().order_by('-date')  # Default: Model.objects.all()
        if "year" in self.request.GET:
            queryset = queryset.filter(date__year=self.request.GET['year'])
        if "month" in self.request.GET:
            queryset = queryset.filter(date__month=self.request.GET['month'])
        if "credit_item" in self.request.GET:
            queryset = queryset.filter(credit_item=CreditItems.objects.get(pk=self.request.GET['credit_item']))
        if "usage" in self.request.GET:
            if self.request.GET['usage'] == "0":
                citem = CreditItems.objects.filter(usage=None)
                queryset = queryset.filter(credit_item__in=citem)
            else:
                usage = Usages.objects.get(pk=self.request.GET['usage'])
                citem = CreditItems.objects.filter(usage=usage)
                queryset = queryset.filter(credit_item__in=citem)
        return queryset


class CreditItemList(PaginationMixin, ListView):
    model = CreditItems
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['usages'] = list()
        for u in Usages.objects.all():
            if CreditItems.objects.filter(usage=u).__len__() > 0:
                res['usages'].append(u)
        return res

    def get_queryset(self):
        queryset = CreditItems.objects.all()  # Default: Model.objects.all()
        if "usage" in self.request.GET:
            if self.request.GET['usage'] == "0":
                queryset = queryset.filter(usage=None)
            else:
                usage = Usages.objects.get(pk=self.request.GET['usage'])
                queryset = queryset.filter(usage=usage)
        return queryset

