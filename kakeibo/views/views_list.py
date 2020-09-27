# coding:utf-8
from django.conf import settings
from django.views.generic import ListView
from django.db.models import Count, Q
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos, Usages, Resources, Credits, CreditItems, Event
# form
from kakeibo.forms import UsageForm, EventForm
# module
from kakeibo.functions.mylib import time_measure


# Create your views here.
@method_decorator(staff_member_required, name='dispatch')
class KakeiboList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Kakeibos
    ordering = ['-date']
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['usages'] = Usages.objects.all()
        res['resources'] = Resources.objects.all()
        res['events'] = Event.objects.filter(is_active=True)
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
        if "event" in self.request.GET:
            queryset = queryset.filter(event=self.request.GET['event'])
        if "search" in self.request.GET:
            queryset = queryset.filter(
                Q(memo__icontains=self.request.GET['search']) |
                Q(event__name__icontains=self.request.GET['search']) |
                Q(event__memo__icontains=self.request.GET['search'])
            )
        return queryset


@method_decorator(staff_member_required, name='dispatch')
class SharedList(PaginationMixin, LoginRequiredMixin, ListView):
    model = SharedKakeibos
    ordering = ['-date']
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['paid_by'] = ["敬士", "朋子"]
        sks = SharedKakeibos.objects.exclude(usage=None).values('usage').annotate(c=Count('pk'))
        res['usages'] = [Usages.objects.get(pk=sk['usage']) for sk in sks]
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


@method_decorator(staff_member_required, name='dispatch')
class CreditList(PaginationMixin, LoginRequiredMixin, ListView):
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


@method_decorator(staff_member_required, name='dispatch')
class CreditItemList(PaginationMixin, LoginRequiredMixin, ListView):
    model = CreditItems
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        cis = CreditItems.objects.exclude(usage=None).values('usage').annotate(c=Count('pk'))
        res['usages'] = [Usages.objects.get(pk=ci['usage']) for ci in cis]
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


@method_decorator(staff_member_required, name='dispatch')
class UsageList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Usages
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['form'] = UsageForm(initial={'date': date.today()})
        return res

    def get_queryset(self):
        queryset = Usages.objects.all()  # Default: Model.objects.all()
        if "search" in self.request.GET:
            queryset = queryset.filter(
                Q(name__icontains=self.request.GET['search'])
            )
        return queryset

    def post(self, request, *args, **kwargs):
        try:
            form = UsageForm(request.POST)
            form.is_valid()
            form.save()
            messages.success(request, "OK")
        except Exception as e:
            messages.error(request, e)
            logger.error(e)
        return redirect('kakeibo:usage_list')


@method_decorator(staff_member_required, name='dispatch')
class EventList(PaginationMixin, LoginRequiredMixin, ListView):
    model = Event
    paginate_by = 20

    @time_measure
    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        res['event_form'] = EventForm(initial={'date': date.today()})
        return res

    def get_queryset(self):
        queryset = Event.objects.all().order_by("-is_active", '-date')  # Default: Model.objects.all()
        return queryset