from kakeibo.models import Kakeibos, Usages, SharedKakeibos, Resources, Credits, CreditItems
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Avg, Q, Count
from django.conf import settings
from datetime import date

# logging
import logging
logger = logging.getLogger("django")


def usage_shared_table(usage_list):
    # 年間
    budget_shared = {"all": settings.BUDGET_TAKA+settings.BUDGET_HOKO}
    suy = SharedKakeibos.objects.filter(date__year=date.today().year) \
        .annotate(month=TruncMonth('date')) \
        .values('month', 'usage').order_by('month') \
        .annotate(sum=Sum('fee'))
    start_month = suy.first()['month'].month
    last_month = suy.last()['month'].month
    data_year = [
        {"month": i, "sum": "", "color": "", "percent": "", "data": list()} for i in range(start_month, last_month + 1)
    ]
    for i in range(last_month + 1 - start_month):
        data_year[i]['data'] = [0 for j in range(len(usage_list))]
    for s in suy:
        name = Usages.objects.get(pk=s['usage']).name
        for u in range(len(usage_list)):
            if name == usage_list[u]:
                data_year[s['month'].month - start_month]['data'][u] = s['sum']
    for i in range(last_month + 1 - start_month):
        data_year[i]['sum'] = sum(data_year[i]['data'])
        data_year[i]["percent"] = data_year[i]['sum'] / (budget_shared['all'] + 30000) * 100
        data_year[i]["color"] = "success" if data_year[i]['sum'] < budget_shared['all'] else "danger"
    data_year.reverse()
    return data_year


def usage_kakeibo_table(usage_list):
    # 年間
    kakeibos = Kakeibos.objects.exclude(usage=None).filter(date__year=date.today().year) \
        .annotate(month=TruncMonth('date')) \
        .values('month', 'usage').order_by('month') \
        .annotate(sum=Sum('fee'))
    smonth = kakeibos.first()['month'].month
    lmonth = kakeibos.last()['month'].month
    data_year = [
        {"month": i, "sum": "", "data": list()} for i in range(smonth, lmonth + 1)
    ]
    for i in range(lmonth + 1 - smonth):
        data_year[i]['data'] = [0 for j in range(len(usage_list))]
    for s in kakeibos:
        name = Usages.objects.get(pk=s['usage']).name
        for u in range(len(usage_list)):
            if name == usage_list[u]:
                data_year[s['month'].month - smonth]['data'][u] = s['sum']
    for i in range(lmonth + 1 - smonth):
        data_year[i]['sum'] = sum(data_year[i]['data'])
    data_year.reverse()
    return data_year


def yearmonth(request):
    if request.GET.get(key="yearmonth") is not None:
        year = request.GET.get(key="yearmonth")[0:4]
        month = request.GET.get(key="yearmonth")[5:]
    else:
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
    if year is None or month is None:
        year = date.today().year
        month = date.today().month
    return year, month
