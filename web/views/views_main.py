# coding:utf-8
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from web.forms import InvestmentForm
from django.contrib import messages
from web.models import Entry, Order, StockValueData, Stock, AssetStatus
from web.functions import mylib_scraping, mylib_asset
from django_celery_results.models import TaskResult
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
class Main(LoginRequiredMixin, TemplateView):
    template_name = "web/main.html"

    def get_context_data(self, **kwargs):
        entrys = Entry.objects.filter(user=self.request.user).exclude(is_closed=False).exclude(is_plan=True).order_by('-pk')[:5]
        open_entrys = Entry.objects.filter(user=self.request.user, is_closed=False).exclude(is_plan=True).order_by('-pk')
        plan_entrys = Entry.objects.filter(user=self.request.user, is_plan=True, is_closed=False).order_by('-pk')
        astatus_list = AssetStatus.objects.filter(user=self.request.user)
        astatus = astatus_list.latest('date') if astatus_list.exists() else None
        checks = mylib_asset.analyse_all(days=15)
        output = {
            "user": self.request.user,
            "entrys": entrys,
            "open_entrys": open_entrys,
            "plan_entrys": plan_entrys,
            "astatus": astatus,
            "investment_form": InvestmentForm(),
            "checks": checks,
        }
        if self.request.user.is_superuser:
            tasks = TaskResult.objects.all()
            output["tasks"] = tasks[:5] if tasks.count() > 5 else tasks
        return output


class Investment(LoginRequiredMixin, FormView):
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

