# coding:utf-8
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos
from kakeibo.forms import KakeiboForm, SharedKakeiboForm


# Create your views here.

class KakeiboDelete(LoginRequiredMixin, DeleteView):
    model = Kakeibos
    form_class = KakeiboForm
    template_name = "kakeibo/kakeibos_delete.html"

    def get_success_url(self):
        return reverse('kakeibo:kakeibo_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, '「{}」を削除しました'.format(self.object))
        return result


class SharedDelete(LoginRequiredMixin, DeleteView):
    model = SharedKakeibos
    form_class = SharedKakeiboForm
    template_name = "kakeibo/sharedkakeibos_delete.html"

    def get_success_url(self):
        return reverse('kakeibo:shared_list')

    def delete(self, request, *args, **kwargs):
        result = super().delete(request, *args, **kwargs)
        messages.success(self.request, '「{}」を削除しました'.format(self.object))
        return result


