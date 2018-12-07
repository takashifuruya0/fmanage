# coding:utf-8
from django.conf import settings
from django.views.generic import CreateView
from django.urls import reverse

# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import Kakeibos, SharedKakeibos
from kakeibo.forms import KakeiboForm, SharedKakeiboForm


# Create your views here.

class KakeiboCreate(CreateView):
    model = Kakeibos
    form_class = KakeiboForm
    template_name = "kakeibo/kakeibos_create.html"

    def get_success_url(self):
        return reverse('kakeibo:kakeibo_detail', kwargs={'pk': self.object.pk})

    # def get_success_url(self):
    #     return reverse('kakeibo:kakeibo_detail', kwargs={'pk': self.object.pk})


class SharedCerate(CreateView):
    model = SharedKakeibos
    form_class = SharedKakeiboForm

    def get_success_url(self):
        return reverse('kakeibo:shared_detail', kwargs={'pk': self.object.pk})

    # def get_success_url(self):
    #     return reverse('kakeibo:shared_detail', kwargs={'pk': self.object.pk})


