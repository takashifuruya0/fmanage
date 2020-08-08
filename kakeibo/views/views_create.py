# coding:utf-8
from django.conf import settings
from django.views.generic import CreateView
from django.urls import reverse
from django.contrib import messages
from datetime import date
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

    def form_valid(self, form):
        # form.save()
        form.save()
        res = super(KakeiboCreate, self).form_valid(form)
        smsg = "New record was registered"
        # shared
        if form.cleaned_data['tag_copy_to_shared']:
            data = {
                'date': form.cleaned_data['date'],
                'fee': form.cleaned_data['fee'],
                'usage': form.cleaned_data['usage'],
                'paid_by': "敬士",
                'memo': form.cleaned_data['memo'],
            }
            SharedKakeibos.objects.create(**data)
            smsg += " and copied to Shared Kakeibo"
        messages.success(self.request, smsg)
        return res

    def get_initial(self, *args, **kwargs):
        initial = super(KakeiboCreate, self).get_initial(**kwargs)
        initial['date'] = date.today()
        initial['event'] = self.request.GET.get('event', None)
        return initial

    def get_success_url(self):
        # return reverse('kakeibo:kakeibo_detail', kwargs={'pk': self.object.pk})
        if self.request.POST.get('source_path', None):
            return self.request.POST['source_path']
        else:
            return reverse('kakeibo:kakeibo_detail', kwargs={'pk': self.object.pk})


class SharedCreate(CreateView):
    model = SharedKakeibos
    form_class = SharedKakeiboForm

    def get_success_url(self):
        return reverse('kakeibo:shared_detail', kwargs={'pk': self.object.pk})



