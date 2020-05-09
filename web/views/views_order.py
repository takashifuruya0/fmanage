# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from web.forms import OrderForm
from web.functions import mylib_asset
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order
# list view, pagination
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from pure_pagination.mixins import PaginationMixin
from django.utils.decorators import method_decorator
# logging
import logging
logger = logging.getLogger("django")


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "web/order_detail.html"
    pk_url_kwarg = "order_id"

    def get_object(self, queryset=None):
        return Order.objects.select_related().get(pk=self.kwargs["order_id"], user=self.request.user)


class OrderUpdate(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    context_object_name = "order"
    pk_url_kwarg = "order_id"
    template_name = "web/order_edit.html"

    def get_success_url(self):
        return reverse("web:order_detail", kwargs={"order_id": self.object.pk})

    def form_invalid(self, form):
        messages.error(self.request, "Not found for order_id = {}".format(self.kwargs['order_id']))
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Order {} was updated".format(self.kwargs['order_id']))
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class OrderList(PaginationMixin, ListView):
    model = Order
    ordering = ['-datetime']
    paginate_by = 20
    template_name = 'web/order_list.html'

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res

    def get_queryset(self):
        queryset = Order.objects.select_related().filter(user=self.request.user).order_by('-datetime')
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


class OrderCreate(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm

    def get_success_url(self):
        return reverse("web:order_detail", kwargs={"order_id": self.object.pk})

    def form_valid(self, form):
        res = super().form_valid(form)
        mylib_asset.order_process(order=self.object, user=self.request.user)
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