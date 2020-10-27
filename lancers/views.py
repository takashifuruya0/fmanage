from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from lancers.models import *
# Create your views here.


class Main(LoginRequiredMixin, TemplateView):
    template_name = "lancers/main.html"

    def get_context_data(self, **kwargs):
        context = super(Main, self).get_context_data(**kwargs)
        context['open_opps'] = Opportunity.objects.filter(status__in=("選定/作業中", "相談中", "提案中"))
        return context
