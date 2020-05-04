# coding:utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.db.models import Q
from django.conf import settings
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from web.forms import OrderForm, EntryForm, StockForm, SBIAlertForm
from web.functions import mylib_scraping, mylib_analysis
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, Stock, StockValueData, StockFinancialData, SBIAlert
from web.functions import mylib_asset
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
        data = mylib_scraping.yf_detail(self.object.code)
        context["current_val"] = data['data']['val'] if data['status'] else None
        context['svds'] = StockValueData.objects.filter(
            stock=context['stock'], date__gte=(date.today()-relativedelta(months=6))
        ).order_by('date')
        context['sfds'] = StockFinancialData.objects.filter(stock=context['stock']).order_by('date')
        df = mylib_analysis.prepare(context['svds'])
        context['df_check'] = mylib_analysis.check(df)
        context['df_trend'] = mylib_analysis.get_trend(df)
        context['entry_form'] = EntryForm(initial={
            "user": self.request.user,
            "stock": context['stock'],
            "border_loss_cut": round(context["current_val"]*0.9),
            "border_profit_determination": round(context["current_val"]*1.1),
        })
        context["sbialert_form"] = SBIAlertForm(initial={"stock": self.object})
        context["sbialerts"] = SBIAlert.objects.filter(stock=self.object, is_active=True)
        # 終値グラフ
        svds = StockValueData.objects.filter(stock=self.object).order_by('date')
        context["svds"] = svds
        # 日付とindex番号の紐付け
        date_list = dict()
        for i, svd in enumerate(svds):
            date_list[svd.date.__str__()] = i
        # 売買注文のグラフ化
        svds_count = svds.count()
        bos_detail = [None for i in range(svds_count)]
        sos_detail = [None for i in range(svds_count)]
        for o in self.object.order_set.all():
            order_date = str(o.datetime.date())
            if order_date in list(date_list.keys()):
                if o.is_buy:
                    bos_detail[date_list[order_date]] = o.val * 10000 if self.object.is_trust else o.val
                else:
                    sos_detail[date_list[order_date]] = o.val * 10000 if self.object.is_trust else o.val
        context["bos_detail"] = bos_detail
        context["sos_detail"] = sos_detail
        # 現在情報を取得
        overview = mylib_scraping.yf_detail(self.object.code)
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
    paginate_by = 20
    template_name = 'web/stock_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['stock_form'] = StockForm()
        return res

    def get_queryset(self):
        queryset = Stock.objects.all().order_by('is_trust', 'code')
        if "search" in self.request.GET:
            queryset = queryset.filter(
                Q(code__icontains=self.request.GET['search']) |
                Q(market__icontains=self.request.GET['search']) |
                Q(industry__icontains=self.request.GET['search']) |
                Q(feature__icontains=self.request.GET['search']) |
                Q(consolidated_business__icontains=self.request.GET['search']) |
                Q(name__icontains=self.request.GET['search'])
            )
        return queryset


class StockCreate(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm

    def get_success_url(self):
        return reverse("web:stock_detail", kwargs={"stock_code": self.object.code})

    def form_valid(self, form):
        """kabuoji3からStockValueDataを取得"""
        res = super().form_valid(form)
        mylib_asset.register_stock_value_data_kabuoji3(self.object.code)
        return res

    def form_invalid(self, form):
        # return super().form_invalid(form)
        messages.error(self.request, form.errors)
        return redirect(reverse("web:stock_list"))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # SVD, SFDの取得
                pass
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return super().post(self, request, *args, **kwargs)