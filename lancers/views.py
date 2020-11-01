from django.shortcuts import render, reverse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, View
from django_currentuser.middleware import get_current_authenticated_user
from lancers.models import *
from lancers.forms import *
from django.contrib import messages
from lancers.functions import mylib_lancers
# DjangoRestFramework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from lancers.serializer import ClientSerializer, CategorySerializer, OpportunitySerializer, OpportunityWorkSerializer
from datetime import date, datetime, timezone, timedelta
import json
import requests
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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


class SyncOppView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        JST = timezone(timedelta(hours=+9), 'JST')
        if settings.ENVIRONMENT == "develop":
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Token {}'.format(settings.TOKEN_DRF)
            }
            success = 0
            added = 0
            error = 0
            error_list = list()
            # Client
            clients = Client.objects.all()
            for client in clients:
                url = "https://www.fk-management.com/drm/lancers/client/{}/".format(client.id)
                raw_data = client.__dict__
                raw_data.pop("_state")
                data = dict()
                for k, v in raw_data.items():
                    data[k] = str(v) if isinstance(v, datetime) or isinstance(v, date) else v
                check = requests.get(url, headers).json()
                if "id" in check.keys():
                    last_updated_at = datetime.strptime(check['last_updated_at'][:-13], "%Y-%m-%dT%H:%M:%S")
                    if client.last_updated_at > last_updated_at.replace(tzinfo=timezone.utc):
                        r = requests.patch(url, json.dumps(data), headers=headers)
                        print("C{}".format(check['id']))
                    else:
                        print("{} {}".format(client.last_updated_at, last_updated_at.replace(tzinfo=JST)))
                        r = None
                else:
                    print("Cnew")
                    url = "https://www.fk-management.com/drm/lancers/client/"
                    r = requests.post(url, json.dumps(data), headers=headers)
                if r is None:
                    continue
                elif r.status_code == 200:
                    success += 1
                elif r.status_code == 201:
                    added += 1
                else:
                    error += 1
                    error_list.append("C{}".format(client.id))
                    print(r.json())
            # Opportunity
            opps = Opportunity.objects.all()
            for opp in opps:
                url = "https://www.fk-management.com/drm/lancers/opportunity/{}/".format(opp.id)
                raw_data = opp.__dict__
                raw_data.pop("_state")
                data = dict()
                for k, v in raw_data.items():
                    data[k] = str(v) if isinstance(v, datetime) or isinstance(v, date) else v
                check = requests.get(url, headers).json()
                if "id" in check.keys():
                    last_updated_at = datetime.strptime(check['last_updated_at'][:-13], "%Y-%m-%dT%H:%M:%S")
                    if opp.last_updated_at > last_updated_at.replace(tzinfo=timezone.utc):
                        r = requests.patch(url, json.dumps(data), headers=headers)
                        print("O{}".format(check['id']))
                    else:
                        print("{} {}".format(opp.last_updated_at, last_updated_at.replace(tzinfo=JST)))
                        r = None
                else:
                    print("Onew")
                    data['client'] = data.pop("client_id")
                    data['category'] = data.pop("category_id")
                    url = "https://www.fk-management.com/drm/lancers/opportunity/"
                    r = requests.post(url, json.dumps(data), headers=headers)
                if r is None:
                    continue
                elif r.status_code == 200:
                    success += 1
                elif r.status_code == 201:
                    added += 1
                else:
                    error += 1
                    error_list.append("O{}".format(opp.id))
                    print(r.json())
                print("{} {}".format(opp.id, r.status_code))
            # OpportunityWork
            ows = OpportunityWork.objects.all()
            for ow in ows:
                url = "https://www.fk-management.com/drm/lancers/opportunitywork/{}/".format(ow.id)
                raw_data = ow.__dict__
                raw_data.pop("_state")
                data = dict()
                for k, v in raw_data.items():
                    data[k] = str(v) if isinstance(v, datetime) or isinstance(v, date) else v
                check = requests.get(url, headers).json()
                if "id" in check.keys():
                    last_updated_at = datetime.strptime(check['last_updated_at'][:-13], "%Y-%m-%dT%H:%M:%S")
                    if opp.last_updated_at > last_updated_at.replace(tzinfo=timezone.utc):
                        r = requests.patch(url, json.dumps(data), headers=headers)
                        print("OW{}".format(check['id']))
                    else:
                        print("{} {}".format(ow.last_updated_at, last_updated_at.replace(tzinfo=JST)))
                        r = None
                else:
                    print("OWnew")
                    data['opportunity'] = data.pop("opportunity_id")
                    url = "https://www.fk-management.com/drm/lancers/opportunitywork/"
                    r = requests.post(url, json.dumps(data), headers=headers)
                if r is None:
                    continue
                elif r.status_code == 200:
                    success += 1
                elif r.status_code == 201:
                    added += 1
                else:
                    error += 1
                    error_list.append("OW{}".format(ow.id))
                    print(r.json())
                print("{} {}".format(opp.id, r.status_code))
            messages.success(request, "Success: {} / Added {} / Error: {}".format(success, added, error))
            if error > 0:
                messages.warning(request, "Error list: {}".format(error_list))
            return redirect('lancers:main')
        else:
            messages.error(request, "Devのみ")
        return redirect('lancers:main')
