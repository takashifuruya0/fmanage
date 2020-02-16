# coding:utf-8
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from web.forms import InvestmentForm
from django.contrib import messages
from django.db import transaction
from web.models import Entry, Order, StockValueData, Stock, AssetStatus
from web.functions import asset_scraping
from django_celery_results.models import TaskResult
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
class Main(TemplateView, LoginRequiredMixin):
    template_name = "web/main.html"

    def get_context_data(self, **kwargs):
        entrys = Entry.objects.filter(user=self.request.user).order_by('-pk')[:5]
        astatus_list = AssetStatus.objects.filter(user=self.request.user)
        astatus = astatus_list.latest('date') if astatus_list.exists() else None
        if self.request.user.is_superuser:
            tasks = TaskResult.objects.all()[:5]
        output = {
            "user": self.request.user,
            "entrys": entrys,
            "tasks": tasks,
            "astatus": astatus,
            "investment_form": InvestmentForm(),
        }
        return output


class Investment(FormView):
    form_class = InvestmentForm

    def get_success_url(self):
        return reverse("web:main")

    def form_valid(self, form):
        astatus = AssetStatus.objects.latest('date')
        astatus.buying_power += form.cleaned_data['value']
        if form.cleaned_data['is_investment']:
            investment_type = "Investment"
            astatus.investment += form.cleaned_data['value']
        else:
            investment_type = "Modification"
        astatus.save()
        messages.info(self.request, "Add ¥{:,} as {}".format(form.cleaned_data['value'], investment_type))
        return super().form_valid(form)

