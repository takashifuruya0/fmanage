# coding:utf-8
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from web.forms import InvestmentForm
from django.contrib import messages
from dateutil import relativedelta
from datetime import date
from web.models import Entry, Order, StockValueData, Stock, AssetStatus, StockAnalysisData, Ipo
from web.functions import mylib_scraping, mylib_asset
from django_celery_results.models import TaskResult
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
class Main(LoginRequiredMixin, TemplateView):
    template_name = "web/main.html"

    def get_context_data(self, **kwargs):
        entrys = Entry.objects.select_related('stock').prefetch_related('order_set').filter(
            user=self.request.user).exclude(is_closed=False).exclude(is_plan=True).order_by('-pk')[:5]
        open_entrys = Entry.objects.select_related('stock').prefetch_related('order_set').filter(
            user=self.request.user, is_closed=False).exclude(is_plan=True).order_by('-pk')
        plan_entrys = Entry.objects.select_related('stock').prefetch_related('order_set').filter(
            user=self.request.user, is_plan=True, is_closed=False).order_by('-pk')
        astatus_list = AssetStatus.objects.filter(user=self.request.user)
        astatus = astatus_list.latest('date') if astatus_list.exists() else None
        # checks = mylib_asset.analyse_all(days=15)
        # Current Total
        if astatus:
            total = astatus.buying_power
            es = Entry.objects.filter(is_closed=False, is_plan=False)
            for e in es:
                current_val = e.stock.current_val()
                val = current_val if current_val else e.stock.latest_val()
                num = e.remaining()
                total += val * num
            try:
                previous_total = AssetStatus.objects.filter(date__lt=astatus.date).latest('date').get_total()
                diff = total - previous_total
            except Exception as e:
                logger.warning("Previous total is not existed")
                diff = 0
        # SAD
        target_date = date.today() - relativedelta.relativedelta(days=7)
        sads = StockAnalysisData.objects.filter(date__gte=target_date).filter(
            Q(val_close_dy_pct__gt=0.05, turnover_dy_pct__gt=1)
            | Q(val_close_dy_pct__lt=-0.05, turnover_dy_pct__gt=1)
            | Q(is_takuri=True)
            # | Q(is_harami=True) | Q(is_tsutsumi=True)
            | Q(is_sanku_tatakikomi=True) | Q(is_age_sanpo=True)
            | Q(is_sage_sanpo=True) | Q(is_sante_daiinsen=True)
        ).order_by('-date')
        # IPO
        ipos = Ipo.objects.exclude(status__icontains="落選").order_by("-pk")
        # output
        output = {
            "user": self.request.user,
            "entrys": entrys,
            "open_entrys": open_entrys,
            "plan_entrys": plan_entrys,
            "astatus": astatus,
            "investment_form": InvestmentForm(),
            # "checks": checks,
            "total": total if astatus else None,
            "diff": diff if astatus else None,
            "sads": sads,
            # ipos
            "ipos": ipos,
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

