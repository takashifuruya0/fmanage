# coding:utf-8
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from web.forms import EntryForm, SBIAlertForm, OrderForm
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from web.models import Entry, Order, StockValueData, SBIAlert, StockAnalysisData
from web.functions import mylib_scraping, mylib_analysis, mylib_asset, mylib_twitter
# list view, pagination
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from pure_pagination.mixins import PaginationMixin
# logging
import logging
logger = logging.getLogger("django")


class EntryUpdate(LoginRequiredMixin, UpdateView):
    model = Entry
    template_name = "web/entry_edit.html"
    form_class = EntryForm

    def get_success_url(self):
        return reverse("web:entry_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        # 各種情報取得
        entry = self.get_object()
        edo = entry.date_open().date() if not entry.is_plan else date.today()
        edc = entry.date_close().date() if entry.is_closed and not entry.is_plan else date.today()
        # days日のマージンでグラフ化範囲を指定
        days = 60
        od = edo - relativedelta(days=days)
        cd = edc + relativedelta(days=days) if entry.is_closed else date.today()
        svds = StockValueData.objects.filter(stock=entry.stock, date__gte=od, date__lte=cd).order_by('date')
        # グラフ化範囲のデータ数
        svds_count = svds.count()
        # 日付とindex番号の紐付け
        date_list = dict()
        for i, svd in enumerate(svds):
            date_list[svd.date.__str__()] = i
        # 売買注文のグラフ化
        bos_detail = [None for i in range(svds_count)]
        sos_detail = [None for i in range(svds_count)]
        for o in entry.order_set.all():
            order_date = str(o.datetime.date())
            if order_date in list(date_list.keys()):
                if o.is_buy:
                    bos_detail[date_list[order_date]] = o.val * 10000 if entry.stock.is_trust else o.val
                else:
                    sos_detail[date_list[order_date]] = o.val * 10000 if entry.stock.is_trust else o.val
        output = {
            "user": self.request.user,
            "entry": entry,
            "svds": svds,
            "bos_detail": bos_detail,
            "sos_detail": sos_detail,
            "od": od,
            "cd": cd,
            "form": self.get_form()
        }
        return output

    def form_valid(self, form):
        messages.info(self.request, "Entry {} was updated".format(self.object.pk))
        return super().form_valid(form)


class EntryList(LoginRequiredMixin, PaginationMixin, ListView):
    model = Entry
    ordering = ['pk']
    paginate_by = 20
    template_name = 'web/entry_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        msg = self.request.GET
        if not settings.ENVIRONMENT == "production":
            messages.info(self.request, msg)
        logger.info(msg)
        res["msg"] = msg
        res["user"] = self.request.user
        res['entry_form'] = EntryForm(initial={"user": self.request.user})
        return res

    def get_queryset(self):
        queryset = Entry.objects.prefetch_related('order_set').select_related().filter(user=self.request.user).order_by('-pk')
        if "is_closed" in self.request.GET:
            is_closed = True if self.request.GET['is_closed'] == "true" else False
            queryset = queryset.filter(is_closed=is_closed)
        if "is_plan" in self.request.GET:
            is_plan = True if self.request.GET['is_plan'] == "true" else False
            queryset = queryset.filter(is_plan=is_plan)
        return queryset

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # entryの統合
                pks = request.POST.getlist('pk')
                entrys = Entry.objects.prefetch_related('order_set').filter(pk__in=pks, user=request.user)
                if request.POST['post_type'] == "merge_entrys":
                    # 最初のEntry
                    first_entry = entrys.first()
                    for entry in entrys:
                        if not entry == first_entry:
                            entry.order_set.all().update(entry=first_entry)
                        if entry.remaining() == 0:
                            entry.delete()
                        else:
                            entry.save()
                    msg = "Entrys {} are merged to Entry {}".format(pks, first_entry.pk)
                elif request.POST['post_type'] == "delete_entrys":
                    entrys.delete()
                    msg = "Entrys {} are deleted".format(pks)
                messages.success(request, msg)
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return self.get(request, *args, **kwargs)


class EntryCreate(LoginRequiredMixin, CreateView):
    model = Entry
    form_class = EntryForm
    template_name = "web/entry_edit.html"
    context_object_name = "entry"

    def get_success_url(self):
        return reverse('web:entry_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "New entry {} was created".format(self.object))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Creating new entry was failed")
        return super().form_invalid(form)


class EntryDelete(LoginRequiredMixin, DeleteView):
    model = Entry
    template_name = "web/entry_delete.html"
    context_object_name = "entry"

    def get_success_url(self):
        return reverse('web:entry_list')

    def delete(self, request, *args, **kwargs):
        ob = self.get_object()
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, '「{}」を削除しました'.format(ob))
        return result


class EntryDetail(LoginRequiredMixin, DetailView):
    model = Entry
    template_name = "web/entry_detail.html"

    def get_object(self, queryset=None):
        return Entry.objects.select_related('stock').prefetch_related(
            'order_set', 'dividend_set').get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        # 各種情報取得
        entry = self.get_object()
        orders_unlinked = Order.objects.filter(entry=None, stock=entry.stock).order_by('datetime')
        orders_linked = entry.order_set.all().order_by('datetime')
        edo = entry.date_open().date() if orders_linked.exists() else date.today()
        edc = entry.date_close().date() if entry.is_closed and not entry.is_plan else date.today()
        # sbialert
        sbialerts = SBIAlert.objects.filter(stock=entry.stock, is_active=True)
        sbialert_form = SBIAlertForm(initial={"stock": entry.stock})
        # days日のマージンでグラフ化範囲を指定
        days = 60
        od = edo - relativedelta(days=days)
        cd = edc + relativedelta(days=days) if entry.is_closed else date.today()
        svds = StockValueData.objects.filter(stock=entry.stock, date__gte=od, date__lte=cd).order_by('date')
        df = mylib_analysis.prepare(svds)
        # df_check = mylib_analysis.check(df)
        df_trend = mylib_analysis.get_trend(df)
        # グラフ化範囲のデータ数
        svds_count = svds.count()
        # 日付とindex番号の紐付け
        date_list = dict()
        for i, svd in enumerate(svds):
            date_list[svd.date.__str__()] = i
        # 売買注文のグラフ化
        bos_detail = [None for i in range(svds_count)]
        sos_detail = [None for i in range(svds_count)]
        for o in entry.order_set.all():
            order_date = str(o.datetime.date())
            if order_date in list(date_list.keys()):
                if o.is_buy:
                    bos_detail[date_list[order_date]] = o.val*10000 if entry.stock.is_trust else o.val
                else:
                    sos_detail[date_list[order_date]] = o.val*10000 if entry.stock.is_trust else o.val
        # graphの判定
        t = date.today()
        if (svds.count() > 0 and svds.latest('date').date == t) or t.isoweekday() > 5:
            if t.isoweekday() <= 5:
                mylib_asset.register_stock_value_data_alt(entry.stock.code)
                svds = StockValueData.objects.filter(stock=entry.stock, date__gte=od, date__lte=cd).order_by('date')
            is_add_graph = False
        else:
            is_add_graph = True
        # 現在情報を取得
        overview_res = mylib_scraping.yf_detail(entry.stock.code)
        if overview_res['status']:
            overview = overview_res['data']
        else:
            svd_latest = StockValueData.objects.filter(stock=entry.stock).latest('date')
            overview = {
                "val": svd_latest.val_close,
                "val_high": svd_latest.val_high,
                "val_low": svd_latest.val_low,
                "val_open": svd_latest.val_open,
                "val_close": svd_latest.val_close,
                "turnover": svd_latest.turnover,
            }
        # OrderFormを追加
        order_form = OrderForm(
            initial={
                "user": self.request.user,
                "is_nisa": entry.stock.is_trust,
                "is_buy": True,
                "entry": entry,
                "commission": 0 if entry.stock.is_trust else None,
                "stock": entry.stock,
            }
        )
        # sads
        sads = StockAnalysisData.objects.filter(stock=entry.stock, date__gte=od, date__lte=cd).order_by('-date')
        # twitter
        twitter = mylib_twitter.Twitter()
        names = entry.stock.name.split("(株)")
        keyword_tweet = "{} {}".format(names[0] if names[0] not in ("(株)", "") else names[1], entry.stock.code)
        tweets = twitter.getTweets(keyword_tweet, 10)
        tweets = tweets['statuses'] if tweets else list()
        # dividend_total
        dividend_total = entry.dividend_set.all().aggregate(val=Sum('val'), tax=Sum('tax'))
        # output
        output = {
            "user": self.request.user,
            "entry": entry,
            "orders_unlinked": orders_unlinked,
            "orders_linked": orders_linked,
            "svds": svds,
            "bos_detail": bos_detail,
            "sos_detail": sos_detail,
            "od": od,
            "cd": cd,
            "df_trend": df_trend,
            "sbialert_form": sbialert_form,
            "sbialerts": sbialerts,
            "is_add_graph": is_add_graph,
            "overview": overview,
            "order_form": order_form,
            "sads": sads,
            "tweets": tweets,
            "keyword_tweet": keyword_tweet,
            "dividend_total": dividend_total,
            "dividend_count": entry.dividend_set.all().count(),
        }
        # res
        return output

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                pks = request.POST.getlist('pk')
                orders = Order.objects.filter(pk__in=pks)
                entry = self.get_object()
                pk = entry.pk
                # link_orders
                if request.POST['post_type'] == "link_orders":
                    orders.update(entry=entry)
                    msg = "Orders {} are linked to Entry {}".format(pks, pk)
                    entry.save()
                    messages.success(request, msg)
                # unlink_orders
                elif request.POST['post_type'] == "unlink_orders":
                    orders.update(entry=None)
                    msg = "Orders {} are unlinked from Entry {}".format(pks, pk)
                    entry.save()
                    messages.success(request, msg)
        except Exception as e:
            logger.error(e)
            messages.error(request, e)
        finally:
            return redirect('web:entry_detail', pk=pk)
