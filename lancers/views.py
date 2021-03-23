from django.shortcuts import render, reverse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, View
from lancers.models import *
from lancers.forms import *
from django.contrib import messages
from lancers.functions import mylib_lancers
# DjangoRestFramework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters import rest_framework as filters
from lancers.serializer import ClientSerializer, CategorySerializer, OpportunitySerializer, OpportunityWorkSerializer
from datetime import date, datetime, timezone, timedelta
import json
import requests
import logging
logger = logging.getLogger("django")
# Create your views here.


class Main(LoginRequiredMixin, TemplateView):
    template_name = "lancers/main.html"

    def get_context_data(self, **kwargs):
        context = super(Main, self).get_context_data(**kwargs)
        context['open_opps'] = Opportunity.objects.filter(status__in=("選定/作業中", "相談中", "提案中")).order_by('status')
        context['opp_form'] = OpportunityForm()
        context['menta_form'] = MentaForm()
        context['services'] = Service.objects.filter(is_active=True).order_by("is_regular", 'val')
        context['DEBUG'] = settings.DEBUG
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


class MentaFormView(LoginRequiredMixin, FormView):
    form_class = MentaForm

    def get_success_url(self):
        return reverse('lancers:main')

    def form_invalid(self, form):
        res = super().form_invalid(form)
        messages.error(self.request, "validation error")
        return res

    def form_valid(self, form):
        res = super().form_valid(form)
        user = get_current_authenticated_user()
        service = form.cleaned_data['service']
        if not form.cleaned_data["client"]:
            c = Client(
                name=form.cleaned_data['client_name'], client_id=form.cleaned_data['client_id'],
                is_nonlancers=True, client_type="MENTA"
            )
            c.save_from_shell(user=user)
        else:
            c = form.cleaned_data["client"]
        o = Opportunity(
            name=service.opportunity_partern.format(client_name=c.name),
            client=c, type="MENTA",
            service=service, val=service.val, val_payment=service.val_payment, is_regular=service.is_regular,
            date_open=form.cleaned_data['date_open'], date_close=form.cleaned_data['date_close'],
            status=form.cleaned_data['status'], category=form.cleaned_data['category'],
            description_opportunity=form.cleaned_data['description_opportunity'],
            date_proposal=form.cleaned_data['date_proposal'],
            description_proposal=form.cleaned_data['description_proposal'],
            num_proposal=form.cleaned_data['num_proposal']
        )
        o.save_from_shell(user=user)
        print(form.cleaned_data['sub_categories'])
        text = "クライアント {} と、商談 {} を作成しました".format(c, o)
        logger.info(text)
        messages.success(self.request, text)
        return res


# =========================
# Filter
# =========================
class OpportunityFilter(filters.FilterSet):
    order_by = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('last_updated_at', 'last_updated_at'),
            ("date_payment", "date_payment"),
            ("date_open", "date_open"),
            ("date_close", "date_close"),
            ("status", "status"),
            ("type", "type"),
            ("name", "name"),
            ("working_time", "working_time"),
            ("val", "val")
        ),
        # labels do not need to retain order
        field_labels={
            'created_at': "作成日",
            'last_updated_at': '最終更新日',
            'date_payment': "支払日",
            "date_open": "開始日",
            "date_close": "終了日",
            "status": "ステータス",
            "type": "タイプ",
            "working_time": "稼働",
            "name": "商談名",
            "val": "金額",
        }
    )

    class Meta:
        model = Opportunity
        fields = ("status", "type", "category", "service", "client")


# =========================
# ViewSet
# =========================
class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Client.objects.all().order_by('-pk')
    serializer_class = ClientSerializer
    filter_fields = (
        "name", 'client_id', "sync_id", "is_nonlancers"
    )


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Category.objects.all().order_by('-pk')
    serializer_class = CategorySerializer
    filter_fields = ('name', "sync_id",)


class OpportunityViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Opportunity.objects.all().order_by('-pk')
    serializer_class = OpportunitySerializer
    filter_fields = (
        "name", 'opportunity_id', "direct_opportunity_id", "sync_id",
        "status", "type"
    )
    filterset_class = OpportunityFilter


class OpportunityWorkViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpportunityWork.objects.all().order_by('-pk')
    serializer_class = OpportunityWorkSerializer
    filter_fields = (
        "sync_id", "opportunity_id",
    )


class SyncToProdView(LoginRequiredMixin, View):
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
                        logger.info("C{}".format(check['id']))
                    else:
                        logger.info("{} {}".format(client.last_updated_at, last_updated_at.replace(tzinfo=JST)))
                        r = None
                else:
                    logger.info("Cnew")
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
                    logger.warning(r.json())
            # Opportunity
            opps = Opportunity.objects.all()
            for opp in opps:
                url = "https://www.fk-management.com/drm/lancers/opportunity/{}/".format(opp.id)
                raw_data = opp.__dict__
                raw_data.pop("_state")
                data = dict()
                for k, v in raw_data.items():
                    data[k] = str(v) if isinstance(v, datetime) or isinstance(v, date) else v
                data['client'] = data.pop("client_id")
                data['category'] = data.pop("category_id")
                check = requests.get(url, headers).json()
                if "id" in check.keys():
                    last_updated_at = datetime.strptime(check['last_updated_at'][:-13], "%Y-%m-%dT%H:%M:%S")
                    if opp.last_updated_at > last_updated_at.replace(tzinfo=JST):
                        r = requests.patch(url, json.dumps(data), headers=headers)
                        logger.info("O{}".format(check['id']))
                    else:
                        logger.info("{} {}".format(opp.last_updated_at, last_updated_at.replace(tzinfo=JST)))
                        r = None
                else:
                    logger.info("Onew")
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
                    logger.warning(r.json())
                logger.info("{} {}".format(opp.id, r.status_code))
            # OpportunityWork
            ows = OpportunityWork.objects.all()
            for ow in ows:
                url = "https://www.fk-management.com/drm/lancers/opportunitywork/{}/".format(ow.id)
                raw_data = ow.__dict__
                raw_data.pop("_state")
                data = dict()
                for k, v in raw_data.items():
                    data[k] = str(v) if isinstance(v, datetime) or isinstance(v, date) else v
                data['opportunity'] = data.pop("opportunity_id")
                check = requests.get(url, headers).json()
                if "id" in check.keys():
                    last_updated_at = datetime.strptime(check['last_updated_at'][:-13], "%Y-%m-%dT%H:%M:%S")
                    if opp.last_updated_at > last_updated_at.replace(tzinfo=JST):
                        r = requests.patch(url, json.dumps(data), headers=headers)
                        logger.info("OW{}".format(check['id']))
                    else:
                        logger.info("{} {}".format(ow.last_updated_at, last_updated_at.replace(tzinfo=JST)))
                        r = None
                else:
                    logger.info("OWnew")
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
                    logger.warning(r.json())
                logger.info("{} {}".format(opp.id, r.status_code))
            messages.success(request, "Success: {} / Added {} / Error: {}".format(success, added, error))
            if error > 0:
                messages.warning(request, "Error list: {}".format(error_list))
            return redirect('lancers:main')
        else:
            messages.error(request, "Devのみ")
        return redirect('lancers:main')
