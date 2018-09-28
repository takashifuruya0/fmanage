# coding:utf-8
from django.conf import settings
from django.views.generic import DetailView
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos


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

