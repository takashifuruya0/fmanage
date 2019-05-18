# coding:utf-8
from django.views.generic import ListView
from pure_pagination.mixins import PaginationMixin
# logging
import logging
logger = logging.getLogger("django")
# model
from asset.models import Orders, Stocks
# module
from kakeibo.functions.mylib import time_measure


# Create your views here.
class OrdersList(PaginationMixin, ListView):
    model = Orders
    ordering = ['-datetime']
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['stock'] = Stocks.objects.all()
        res['order_type'] = ["現物買", "現物売"]
        return res

    def get_queryset(self):
        queryset = Orders.objects.all().order_by('-datetime')  # Default: Model.objects.all()
        if "stock" in self.request.GET:
            queryset = queryset.filter(stock=Stocks.objects.get(pk=self.request.GET['stock']))
        if "order_type" in self.request.GET:
            queryset = queryset.filter(order_type=self.request.GET['order_type'])
        return queryset

