# coding:utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.conf import settings
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from web.forms import OrderForm, EntryForm, StockForm, SBIAlertForm
from web.functions import asset_scraping, asset_analysis
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, Stock, StockValueData, StockFinancialData, SBIAlert
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
        context = super().get_context_data(**kwargs)
        data = asset_scraping.yf_detail(self.object.code)
        context["current_val"] = data['data']['val'] if data['status'] else None
        context['svds'] = StockValueData.objects.filter(
            stock=context['stock'], date__gte=(date.today()-relativedelta(months=6))
        ).order_by('date')
        context['sfds'] = StockFinancialData.objects.filter(stock=context['stock']).order_by('date')
        df = asset_analysis.prepare(context['svds'])
        context['df_trend'] = asset_analysis.get_trend(df)
        context['entry_form'] = EntryForm(initial={
            "user": self.request.user,
            "stock": context['stock'],
            "border_loss_cut": context["current_val"]*1.05,
            "border_profit_determination": context["current_val"]*0.9,
        })
        context["sbialert_form"] = SBIAlertForm(initial={"stock": self.object})
        context["sbialerts"] = SBIAlert.objects.filter(stock=self.object, is_active=True)
        # 現在情報を取得
        overview = asset_scraping.yf_detail(self.object.code)
        if overview['status']:
            context['overview'] = overview['data']
        return context


class StockUpdate(LoginRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    context_object_name = "stock"
    pk_url_kwarg = "stock_code"
    template_name = "web/stock_edit.html"

    def get_success_url(self):
        return reverse("web:stock_detail", kwargs={"stock_code": self.kwargs['stock_code']})

    def get_object(self, queryset=None):
        return Stock.objects.prefetch_related('order_set', "entry_set").get(code=self.kwargs['stock_code'])

    def form_invalid(self, form):
        print(form.errors)
        messages.error(self.request, "Not found or not authorized to access it")
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Stock {} was updated".format(self.get_object()))
        return super().form_valid(form)


class StockList(LoginRequiredMixin, PaginationMixin, ListView):
    model = Stock
    ordering = ['code']
    paginate_by = 20
    template_name = 'web/stock_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['stock_form'] = StockForm()
        return res

    def get_queryset(self):
        queryset = Stock.objects.all().order_by('code')
        return queryset


class StockCreate(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm

    def get_success_url(self):
        return reverse("web:stock_detail", kwargs={"stock_code": self.object.code})

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                pass
                # SVD, SFDの取得
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return super().post(self, request, *args, **kwargs)