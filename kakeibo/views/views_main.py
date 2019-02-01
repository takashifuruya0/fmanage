# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.conf import settings
from django.db.models import Q
from dateutil.relativedelta import relativedelta
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import *
from datetime import date
# function
from kakeibo.functions import mylib
from kakeibo.functions.mylib import time_measure
from kakeibo.functions import process_kakeibo


# Create your views here.


@login_required
@time_measure
def dashboard(request):
    today = date.today()
    # kakeibo
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year)
    ekakeibos = kakeibos.exclude(Q(way='振替') | Q(way='収入') | Q(way="支出（クレジット）"))
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    expense = mylib.cal_sum_or_0(ekakeibos)

    # status, progress_bar
    pb_kakeibo, status_kakeibo = process_kakeibo.kakeibo_status(income, expense)

    # way
    ways_sum = kakeibos.values('way').annotate(Sum('fee'))
    current_way = dict()
    for w in ways_sum:
        current_way[w['way']] = w['fee__sum']
    if "振替" in current_way.keys():
        current_way.pop("振替")
        logger.info("振替 is poped out")

    # resource
    current_resource = dict()
    resources_chart = list()
    for rs in Resources.objects.all():
        val = rs.current_val()
        move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
        val2 = val - move_to + move_from
        if val is not 0:
            current_resource[rs.name] = val
            tmp = {"name": rs.name, "this_month": val, "last_month": val2}
            resources_chart.append(tmp)

    # usage
    current_usage = ekakeibos.values('usage__name').annotate(sum=Sum('fee')).order_by("sum").reverse()
    logger.info(current_usage)

    # shared
    seisan = mylib.seisan(today.year, today.month)
    budget_shared = {
        "t": seisan['budget']['taka'],
        "h": seisan['budget']['hoko'],
        "all": seisan['budget']['hoko'] + seisan['budget']['taka']
    }
    expense_shared = {
        "t": seisan['payment']['taka'],
        "h": seisan['payment']['hoko'],
        "all": seisan['payment']['hoko'] + seisan['payment']['taka']
    }
    shared = SharedKakeibos.objects.filter(date__month=today.month, date__year=today.year)
    inout_shared = seisan["inout"]
    rb_name = seisan['status']
    move = seisan['seisan']

    # 赤字→精算あり
    if rb_name == "赤字":
        status_shared = "danger"
        pb_shared = {"in": int(budget_shared['all'] / expense_shared['all'] * 100), "out": 100}
    else:
        status_shared = "primary"
        pb_shared = {"in": 100, "out": int(expense_shared['all'] / budget_shared['all'] * 100)}

    # shared_grouped_by_usage
    shared_grouped_by_usage = shared.values('usage__name').annotate(sum=Sum('fee')).order_by("sum").reverse()
    logger.info(shared_grouped_by_usage)

    # chart.js
    data = {
        "現金精算": [0, seisan['seisan'], 0, 0],
        "予算": [seisan['budget']['hoko'], 0, seisan['budget']['taka'], 0],
        "支払": [0, seisan['payment']['hoko'], 0, seisan['payment']['taka']],
        rb_name: seisan['rb'],
    }
    labels = ["朋子予算", "朋子支払", "敬士予算", "敬士支払"]
    bar_eom = {"data": data, "labels": labels}

    output = {
        "today": today,
        # kakeibo
        "inout": income-expense,
        "income": income,
        "expense": expense,
        "current_way": current_way,
        "current_resource": current_resource,
        "resources": resources_chart,
        "current_usage": current_usage,
        # shared
        "inout_shared": inout_shared,
        "budget_shared": budget_shared,
        "expense_shared": expense_shared,
        "move": move,
        "shared_grouped_by_usage": shared_grouped_by_usage,
        "bar_eom": bar_eom,
        # progress bar and status
        "pb": {"kakeibo": pb_kakeibo, "shared": pb_shared},
        "status": {"kakeibo": status_kakeibo, "shared": status_shared},
    }
    logger.info("output: " + str(output))
    return TemplateResponse(request, 'kakeibo/dashboard.html', output)


@login_required
def form_kakeibo(request):
    url = settings.URL_FORM
    # return redirect(url)
    output = {"url": url}
    return TemplateResponse(request, 'kakeibo/form.html', output)


@login_required
def form_shared(request):
    url = settings.URL_SHAREDFORM
    # return redirect(url)
    output = {"url": url}
    return TemplateResponse(request, 'kakeibo/form.html', output)


@login_required
@time_measure
def mine(request):
    # 貯金扱いの口座
    saving_account = [r.name for r in Resources.objects.filter(is_saving=True)]
    # check year and month from GET parameter
    year, month = process_kakeibo.yearmonth(request)

    kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year)
    ekakeibos = kakeibos.exclude(Q(way='振替') | Q(way='収入') | Q(way="支出（クレジット）"))
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    expense = mylib.cal_sum_or_0(ekakeibos)

    # status, progress_bar
    pb_kakeibo, status_kakeibo = process_kakeibo.kakeibo_status(income, expense)

    # way
    ways_sum = kakeibos.values('way').annotate(Sum('fee'))
    ways = list()
    for w in ways_sum:
        if w['way'] != "振替":
            tmp = {"val": w['fee__sum'], "name": w['way']}
            ways.append(tmp)
    # saved
    rs_saved = Resources.objects.filter(name__in=saving_account)
    move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to__in=rs_saved))
    move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from__in=rs_saved))
    saved = move_to - move_from

    # resource
    resources = Resources.objects.all()

    # usage
    usages_chart = ekakeibos.values('usage__name').annotate(sum=Sum('fee')).order_by("sum").reverse()

    # resources_year
    resources_year_chart, months_chart = process_kakeibo.resources_year_rev(12)
    logger.info(resources_year_chart)

    # kakeibo-usage
    usage_list = [u.name for u in Usages.objects.filter(is_expense=True)]
    kakeibo_usage = process_kakeibo.usage_kakeibo_table(usage_list)

    # Consolidated_usages: dict --> [(name, val),(name, val),(name, val),...]
    consolidated_usages_chart = sorted(process_kakeibo.consolidated_usages().items(), key=lambda x: -x[1])
    cash_usages_chart = sorted(process_kakeibo.cash_usages().items(), key=lambda x: -x[1])

    # total
    total = sum([r.current_val() for r in Resources.objects.all()])
    total_saved = sum(rs.current_val() for rs in rs_saved)

    # 1年間での推移
    saved_one_year_ago = 0
    for ryc in resources_year_chart:
        if ryc['name'] in saving_account:
            saved_one_year_ago = ryc["val"][0]
            break
    change = {
        "total":  total - sum([i['val'][0] for i in resources_year_chart]),
        "total_saved": total_saved - saved_one_year_ago
    }

    # 年間の収入・支出
    inouts_grouped_by_months = process_kakeibo.inouts_grouped_by_months()
    usages_grouped_by_months = process_kakeibo.usages_grouped_by_months()

    # output
    output = {
        "today": {"year": year, "month": month},
        # status
        "status": status_kakeibo,
        "saved": saved,
        "inout": income - expense,
        # progress_bar
        "pb_kakeibo": pb_kakeibo,
        "income": income,
        "expense": expense,
        # current list
        "ways": ways,
        # table
        "resources_table": resources,
        # chart js
        "usages_chart": usages_chart,
        "resources_year_chart": resources_year_chart,
        "months_chart": months_chart,
        "consolidated_usages_chart": consolidated_usages_chart,
        # kus
        "kakeibo_usage_table": kakeibo_usage,
        "usage_list": usage_list,
        # total
        "total": total,
        "total_saved": total_saved,
        "change": change,
        # igbn
        "inouts_grouped_by_months": inouts_grouped_by_months,
        # cash_usages_chart
        "cash_usages_chart": cash_usages_chart,
    }
    return TemplateResponse(request, 'kakeibo/mine.html', output)


@login_required
@time_measure
def shared(request):
    # check year and month from GET parameter
    year, month = process_kakeibo.yearmonth(request)

    # shared
    seisan = mylib.seisan(year, month)
    budget_shared = {
        "t": seisan['budget']['taka'],
        "h": seisan['budget']['hoko'],
        "all": seisan['budget']['hoko'] + seisan['budget']['taka']
    }
    expense_shared = {
        "t": seisan['payment']['taka'],
        "h": seisan['payment']['hoko'],
        "all": seisan['payment']['hoko'] + seisan['payment']['taka']
    }
    shared = SharedKakeibos.objects.filter(date__month=month, date__year=year)
    inout_shared = seisan["inout"]
    rb_name = seisan['status']
    move = seisan['seisan']

    # 赤字→精算あり
    if rb_name == "赤字":
        status_shared = "danger"
        pb_shared = {"in": int(budget_shared['all'] / expense_shared['all'] * 100), "out": 100}
    else:
        status_shared = "primary"
        pb_shared = {"in": 100, "out": int(expense_shared['all'] / budget_shared['all'] * 100)}

    # shared_grouped_by_usage
    shared_usages = shared.values('usage__name').annotate(Sum('fee'))

    # chart.js
    data = {
        "現金精算": [0, seisan['seisan'], 0, 0],
        "予算": [seisan['budget']['hoko'], 0, seisan['budget']['taka'], 0],
        "支払": [0, seisan['payment']['hoko'], 0, seisan['payment']['taka']],
        rb_name: seisan['rb'],
    }
    labels = ["朋子予算", "朋子支払", "敬士予算", "敬士支払"]
    bar_eom = {"data": data, "labels": labels}

    # 年間
    usage_list = ["家賃", "食費", "日常消耗品", "ガス", "電気", "水道", "その他"]
    data_year = process_kakeibo.usage_shared_table(usage_list)

    # who paid ?
    who_paid = shared.values('usage__name', 'paid_by').annotate(Sum('fee'))

    # output
    output = {
        "today": {"year": year, "month": month},
        # status
        "status": status_shared,
        # progress_bar
        "pb_shared": pb_shared,
        # shared
        "inout": inout_shared,
        "budget": budget_shared,
        "expense": expense_shared,
        "move": move,
        "shared_usages": shared_usages,
        "bar_eom": bar_eom,
        # table
        "data_year": data_year,
        "usage_list": usage_list,
        # who_paid
        "who_paid": who_paid,
    }
    return TemplateResponse(request, 'kakeibo/shared.html', output)


@login_required
@time_measure
def credit(request):
    # check year and month from GET parameter
    year, month = process_kakeibo.yearmonth(request)
    # 今月のクレジット利用履歴と合計値
    credits_month = Credits.objects.filter(debit_date__year=year, debit_date__month=month).order_by('-fee')
    credits_sum = sum([ci.sum_credit() for ci in CreditItems.objects.all()])

    # CreditItemとusage別合計
    res_credits = dict()
    sum_usage = dict()
    for citem in CreditItems.objects.all():
        temp = {
            'name': citem.name,
            'sum': citem.sum_credit(),
            'avg': citem.avg_credit(),
            'count': citem.count_credit(),
        }
        # usageが登録されていない場合を考慮
        if citem.usage:
            temp['usage'] = citem.usage.name
            tag = citem.usage.name
        else:
            temp['usage'] = ""
            tag = "その他"

        if tag in sum_usage.keys():
            sum_usage[tag] += temp['sum']
        else:
            sum_usage[tag] = temp['sum']
        res_credits[citem.pk] = temp

    # credit_month_sum
    credits_month_sum = sum([cm.fee for cm in credits_month])

    # 支出項目の円表示
    res_sum_usage = dict()
    for k, v in sorted(sum_usage.items(), key=lambda x: -x[1]):
        res_sum_usage[k] = {"sum": v, "name": k}

    # Sumの降順に並び替え
    res_credits = sorted(res_credits.items(), key=lambda x: -x[1]['sum'])
    res_sum_usage = sorted(res_sum_usage.items(), key=lambda x: -x[1]['sum'])

    # count
    credits_month_count = credits_month.__len__()

    # return
    output = {
        "today": {"year": year, "month": month},
        "credits": res_credits,
        "sum_usage": res_sum_usage,
        "credits_sum": credits_sum,
        "credits_month": credits_month,
        "credits_month_sum": credits_month_sum,
        "credits_month_count": credits_month_count,
    }

    return TemplateResponse(request, 'kakeibo/cdashboard.html', output)


@time_measure
def test(request):
    today = date(2019,1,31)
    monthly_kakeibos = Kakeibos.objects.filter(
        date__year=today.year, date__month=today.month
    ).values('way', 'usage__name', "usage__color__name").annotate(sum=Sum('fee')).order_by("-sum")

    ways = ("支出（現金）", "支出（クレジット）", "引き落とし",)
    # 支払い方法別の合計
    monthly_sum_by_way = Kakeibos.objects.filter(
        date__year=today.year, date__month=today.month, way__in=ways
    ).values('way').annotate(sum=Sum('fee')).order_by("-sum")
    # 支払い方法別の内訳
    monthly_details_by_way = [dict() for w in ways]
    for i, w in enumerate(ways):
        monthly_details_by_way[i]["name"] = w
        monthly_details_by_way[i]["data"] = monthly_kakeibos.filter(way=w)
    # 用途別
    monthly_expense_sum_by_usage = Kakeibos.objects.filter(
        date__year=today.year, date__month=today.month, usage__is_expense=True
    ).values('usage__name', "usage__color__name").annotate(sum=Sum('fee')).order_by("-sum")
    monthly_income_sum_by_usage = Kakeibos.objects.filter(
        date__year=today.year, date__month=today.month, usage__is_expense=False
    ).values('usage__name', "usage__color__name").annotate(sum=Sum('fee')).order_by("-sum")

    # return
    output = {
        "monthly_details_by_way": monthly_details_by_way,
        "monthly_sum_by_way": monthly_sum_by_way,
        "monthly_expense_sum_by_usage": monthly_expense_sum_by_usage,
        "monthly_income_sum_by_usage": monthly_income_sum_by_usage,
    }
    return TemplateResponse(request, 'kakeibo/test.html', output)


