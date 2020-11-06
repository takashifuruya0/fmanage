# coding:utf-8
from django.conf import settings
from django.views.generic import DetailView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from pure_pagination import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.db.models import Sum, Count, Avg
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos, Usages, Resources, Credits, CreditItems, Event
from kakeibo.forms import KakeiboForm, SharedKakeiboForm, CreditForm, CreditItemForm, UsageForm, EventForm


# Create your views here.

# @method_decorator(staff_member_required, name='dispatch')
class KakeiboDetail(LoginRequiredMixin, DetailView):
    model = Kakeibos

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


class SharedDetail(DetailView):
    model = SharedKakeibos

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


# @method_decorator(staff_member_required, name='dispatch')
class CreditDetail(LoginRequiredMixin, DetailView):
    model = Credits

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


# @method_decorator(staff_member_required, name='dispatch')
class CreditItemDetail(LoginRequiredMixin, DetailView):
    model = CreditItems

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


# @method_decorator(staff_member_required, name='dispatch')
class UsageDetail(LoginRequiredMixin, DetailView):
    model = Usages

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


# @method_decorator(staff_member_required, name='dispatch')
class EventDetail(PaginationMixin, MultipleObjectMixin, LoginRequiredMixin, DetailView):
    model = Event
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = Kakeibos.objects.filter(event=self.get_object(), is_active=True).order_by('-date')
        context = super(EventDetail, self).get_context_data(object_list=object_list, **kwargs)
        return context


# @method_decorator(staff_member_required, name='dispatch')
class KakeiboUpdate(LoginRequiredMixin, UpdateView):
    model = Kakeibos
    form_class = KakeiboForm

    def get_success_url(self):
        return reverse('kakeibo:kakeibo_detail', kwargs={'pk': self.object.pk})


class SharedUpdate(UpdateView):
    model = SharedKakeibos
    form_class = SharedKakeiboForm

    def get_success_url(self):
        return reverse('kakeibo:shared_detail', kwargs={'pk': self.object.pk})


# @method_decorator(staff_member_required, name='dispatch')
class CreditUpdate(LoginRequiredMixin, UpdateView):
    model = Credits
    form_class =CreditForm

    def get_success_url(self):
        return reverse('kakeibo:credit_detail', kwargs={'pk': self.object.pk})


# @method_decorator(staff_member_required, name='dispatch')
class CreditItemUpdate(LoginRequiredMixin, UpdateView):
    model = CreditItems
    form_class = CreditItemForm

    def get_success_url(self):
        return reverse('kakeibo:credit_item_detail', kwargs={'pk': self.object.pk})


# @method_decorator(staff_member_required, name='dispatch')
class UsageUpdate(LoginRequiredMixin, UpdateView):
    model = Usages
    form_class = UsageForm

    def get_success_url(self):
        return reverse('kakeibo:usage_detail', kwargs={'pk': self.object.pk})


# @method_decorator(staff_member_required, name='dispatch')
class EventUpdate(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm

    def get_success_url(self):
        return reverse('kakeibo:event_detail', kwargs={'pk': self.object.pk})
