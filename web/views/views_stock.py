# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.conf import settings
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from web.forms import OrderForm, EntryForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, Stock, StockValueData, StockFinancialData
# list view, pagination
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from pure_pagination.mixins import PaginationMixin
# logging
import logging
logger = logging.getLogger("django")


class StockDetail(LoginRequiredMixin, DetailView):
    template_name = "web/stock_detail.html"
    model = Stock
    pk_url_kwarg = "stock_code"
    context_object_name = "stock"

    def get_object(self, queryset=None):
        return Stock.objects.prefetch_related('order_set', "entry_set").get(code=self.kwargs['stock_code'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['svds'] = StockValueData.objects.filter(stock=context['stock'], date__gte=(date.today() - relativedelta(months=6))).order_by(
            'date')
        context['sfds'] = StockFinancialData.objects.filter(stock=context['stock']).order_by('date')
        context['entry_form'] = EntryForm(initial={"user": self.request.user, "stock": context['stock']})
        return context


@login_required
def stock_edit(request, stock_code):
    try:
        stock = Stock.objects.prefetch_related('entry_set', "order_set").get(code=stock_code)
    except Exception as e:
        logger.error(e.args)
        messages.error(request, "Not found or not authorized to access it")
        return redirect('web:main')
    if request.method == "POST":
        return redirect('web:stock_detail', stock_code=stock_code)
    elif request.method == "GET":
        output = {
            "stock": stock,
        }
        return TemplateResponse(request, "web/stock_edit.html", output)


class StockList(LoginRequiredMixin, PaginationMixin, ListView):
    model = Stock
    ordering = ['code']
    paginate_by = 20
    template_name = 'web/stock_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res

    def get_queryset(self):
        queryset = Stock.objects.all().order_by('code')
        return queryset

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                pass
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return self.get(request, *args, **kwargs)
