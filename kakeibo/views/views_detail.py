# coding:utf-8
from django.conf import settings
from django.views.generic import DetailView, UpdateView
from django.urls import reverse

# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos, Usages, Resources, Credits, CreditItems
from kakeibo.forms import KakeiboForm, SharedKakeiboForm, CreditForm, CreditItemForm


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
