from django.shortcuts import render, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from django_currentuser.middleware import get_current_authenticated_user
from lancers.models import *
from lancers.forms import *
from django.contrib import messages
from lancers.functions import mylib_lancers
# DjangoRestFramework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from lancers.serializer import ClientSerializer, CategorySerializer, OpportunitySerializer, OpportunityWorkSerializer
# Create your views here.


class Main(LoginRequiredMixin, TemplateView):
    template_name = "lancers/main.html"

    def get_context_data(self, **kwargs):
        context = super(Main, self).get_context_data(**kwargs)
        context['open_opps'] = Opportunity.objects.filter(status__in=("選定/作業中", "相談中", "提案中"))
        context['opp_form'] = OpportunityForm()
        return context


class OpportunityFormView(LoginRequiredMixin, FormView):
    form_class = OpportunityForm

    def get_success_url(self):
        messages.success(self.request, "Success")
        return reverse('lancers:main')

    def form_valid(self, form):
        res = super().form_valid(form)
        mylib_lancers.create_opportunity2(
            oppid=form.cleaned_data['oppid'],
            u=get_current_authenticated_user(),
            type_opp=form.cleaned_data['type_opp'],
            category_name=form.cleaned_data['category_id'].name,
            status=form.cleaned_data['status'],
            memo=form.cleaned_data['memo'],
        )
        return res


class ClientViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OpportunityViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer


class OpportunityWorkViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpportunityWork.objects.all()
    serializer_class = OpportunityWorkSerializer
