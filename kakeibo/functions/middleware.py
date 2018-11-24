from kakeibo.models import Kakeibos, Usages, SharedKakeibos, Resources, Credits, CreditItems
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Avg, Q, Count
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
# function
from kakeibo.functions import mylib
from kakeibo.functions.mylib import time_measure


# logging
import logging
logger = logging.getLogger("django")


@time_measure
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
    usage_names = {u.pk: u.name for u in Usages.objects.all()}
    for s in suy:
        name = usage_names[s['usage']]
        for u in range(len(usage_list)):
            if name == usage_list[u]:
                data_year[s['month'].month - start_month]['data'][u] = s['sum']
    for i in range(last_month + 1 - start_month):
        data_year[i]['sum'] = sum(data_year[i]['data'])
        data_year[i]["percent"] = data_year[i]['sum'] / (budget_shared['all'] + 30000) * 100
        data_year[i]["color"] = "success" if data_year[i]['sum'] < budget_shared['all'] else "danger"
    data_year.reverse()
    return data_year


@time_measure
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
    usage_names = {u.pk: u.name for u in Usages.objects.all()}
    for s in kakeibos:
        name = usage_names[s['usage']]
        for u in range(len(usage_list)):
            if name == usage_list[u]:
                data_year[s['month'].month - smonth]['data'][u] = s['sum']
    for i in range(lmonth + 1 - smonth):
        data_year[i]['sum'] = sum(data_year[i]['data'])
    data_year.reverse()
    return data_year


@time_measure
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


@time_measure
def consolidated_usages():
    # responseの型を設定
    usages = Usages.objects.all()
    res = {u.name: 0 for u in usages}
    # Kakeibos
    kus = Kakeibos.objects.exclude(usage=None).values('usage').annotate(sum=Sum('fee'))
    uname = {u.pk: u.name for u in Usages.objects.all()}
    for ku in kus:
        name = uname[ku['usage']]
        res[name] += ku['sum']
    # Credits
    cis = CreditItems.objects.all()
    for ci in cis:
        c_sum = Credits.objects.filter(credit_item=ci).aggregate(Sum('fee'))['fee__sum']
        try:
            res[ci.usage.name] += c_sum
        # CreditItemsとUsagesの紐づけがされていない場合→その他へ
        except Exception as e:
            res["その他"] += c_sum
    # クレジットは削除
    res.pop("クレジット（個人）")
    res.pop("クレジット（家族）")
    # is_expense=False は削除
    for u in usages:
        if u.is_expense is False:
            res.pop(u.name)
    # 並び替え
    # res = dict(sorted(res.items(), key=lambda x: -x[1]))
    return res


@time_measure
def resources_year_rev(num=12):
    resources = Resources.objects.all()
    resources_year_chart = [{"name": r.name, "val": [r.current_val() for j in range(num)]} for r in resources]

    # months_chart: monthの古い順リスト
    today = date.today()
    months = [(today + relativedelta(months=-i)) for i in range(num)]
    months_chart = [(str(m.year) + "/" + str(m.month)) for m in months]
    months_chart.reverse()

    start_month = today + relativedelta(months=-num)
    kfs = Kakeibos.objects.exclude(move_from=None).exclude(date__lt=start_month)\
        .annotate(month=TruncMonth('date'))\
        .values('month', 'move_from').annotate(sum=Sum('fee'))
    kts = Kakeibos.objects.exclude(move_to=None).exclude(date__lt=start_month)\
        .annotate(month=TruncMonth('date'))\
        .values('month', 'move_to').annotate(sum=Sum('fee'))

    # resources_year_chartにおける、resources の順番
    resources_order = dict()
    cnt = 0
    resource_ids = {r.name: r.pk for r in resources}
    for r in resources_year_chart:
        resources_order[resource_ids[r['name']]] = cnt
        cnt += 1

    # xn = current_val - sum(t)^c_(n+1) + sum(f)^c_(n+1)
    for kf in kfs:
        # 今月と対象月の差分月数
        diff = (today.year - kf['month'].year) * 12 + (today.month - kf['month'].month)
        # diff = 0 ~ num-2
        if diff >= num-1:
            continue
        else:
            cnt_f = resources_order[kf['move_from']]
            for i in range(0, num-diff-1):
                resources_year_chart[cnt_f]['val'][i] += kf['sum']

    for kt in kts:
        diff = (today.year - kt['month'].year) * 12 + (today.month - kt['month'].month)
        if diff >= num:
            continue
        else:
            cnt_t = resources_order[kt['move_to']]
            for i in range(0, num-diff-1):
                resources_year_chart[cnt_t]['val'][i] -= kt['sum']

    return resources_year_chart, months_chart


@time_measure
def kakeibo_status(income, expense):
    # status, progress_bar
    try:
        if income > expense:
            status_kakeibo = "primary"
            pb_kakeibo = {"in": 100, "out": int(expense / income * 100)}
        else:
            status_kakeibo = "danger"
            pb_kakeibo = {"in": int(income / expense * 100), "out": 100}
    except Exception as e:
        logger.error("Failed to set status and progress_bar")
        status_kakeibo = "primary"
        pb_kakeibo = {"in": 100, "out": 100}
    return pb_kakeibo, status_kakeibo

