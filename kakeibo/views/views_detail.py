# coding:utf-8
from django.conf import settings
from django.views.generic import DetailView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from pure_pagination import PaginationMixin
from django.urls import reverse
from django.db.models import Sum, Count, Avg
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos, Usages, Resources, Credits, CreditItems, Event
from kakeibo.forms import KakeiboForm, SharedKakeiboForm, CreditForm, CreditItemForm, UsageForm, EventForm


# Create your views here.

class KakeiboDetail(DetailView):
    model = Kakeibos

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


class SharedDetail(DetailView):
    model = SharedKakeibos

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


class CreditDetail(DetailView):
    model = Credits

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


class CreditItemDetail(DetailView):
    model = CreditItems

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


class UsageDetail(DetailView):
    model = Usages

    def get_context_data(self, **kwargs):
        res = super().get_context_data(**kwargs)
        return res


class EventDetail(PaginationMixin, MultipleObjectMixin, DetailView):
    model = Event
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = Kakeibos.objects.filter(event=self.get_object(), is_active=True).order_by('-date')
        context = super(EventDetail, self).get_context_data(object_list=object_list, **kwargs)
        return context


class KakeiboUpdate(UpdateView):
    model = Kakeibos
    form_class = KakeiboForm

    def get_success_url(self):
        return reverse('kakeibo:kakeibo_detail', kwargs={'pk': self.object.pk})


class SharedUpdate(UpdateView):
    model = SharedKakeibos
    form_class = SharedKakeiboForm

    def get_success_url(self):
        return reverse('kakeibo:shared_detail', kwargs={'pk': self.object.pk})


class CreditUpdate(UpdateView):
    model = Credits
    form_class =CreditForm

    def get_success_url(self):
        return reverse('kakeibo:credit_detail', kwargs={'pk': self.object.pk})


class CreditItemUpdate(UpdateView):
    model = CreditItems
    form_class = CreditItemForm

    def get_success_url(self):
        return reverse('kakeibo:credit_item_detail', kwargs={'pk': self.object.pk})


class UsageUpdate(UpdateView):
    model = Usages
    form_class = UsageForm

    def get_success_url(self):
        return reverse('kakeibo:usage_detail', kwargs={'pk': self.object.pk})


class EventUpdate(UpdateView):
    model = Event
    form_class = EventForm

    def get_success_url(self):
        return reverse('kakeibo:event_detail', kwargs={'pk': self.object.pk})
