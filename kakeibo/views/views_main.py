# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.db.models import Avg, Sum, Count, Q
from django.views.generic import ListView
from dateutil.relativedelta import relativedelta
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import *
# module
import requests, json
from datetime import datetime, date, timedelta
# function
from kakeibo.functions import update_records, money, figure, mylib
from kakeibo.functions.mylib import time_measure
from kakeibo.functions import middleware
# grouped by month
from django.db.models.functions import TruncMonth

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
    pb_kakeibo, status_kakeibo = middleware.kakeibo_status(income, expense)

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
        # current_valがあれば早い
        if rs.current_val is not None:
            val = rs.current_val
            move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
            val2 = val - move_to + move_from
        else:
            move_to = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_from=rs))
            val = rs.initial_val + move_to - move_from
            move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
            val2 = val - move_to + move_from
        if val is not 0:
            current_resource[rs.name] = val
            tmp = {"name": rs.name, "this_month": val, "last_month": val2}
            resources_chart.append(tmp)

    # usage
    current_usage = list()
    cash_usages = ekakeibos.values('usage').annotate(sum=Sum('fee'))
    usage_names = {u.pk: u.name for u in Usages.objects.all()}
    for cu in cash_usages:
        name = usage_names[cu['usage']]
        val = cu['sum']
        current_usage.append({"name": name, "val": val})
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
    shared_usages = shared.values('usage').annotate(sum=Sum('fee'))
    shared_grouped_by_usage = list()
    if shared_usages.__len__() != 0:
        for su in shared_usages:
            tmp = dict()
            tmp['name'] = usage_names[su['usage']]
            tmp['val'] = su['sum']
            shared_grouped_by_usage.append(tmp)
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

    # msg
    smsg = ""

    output = {
        "today": today,
        "smsg": smsg,
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
    return render(request, 'kakeibo/dashboard.html', output)


@login_required
def form_kakeibo(request):
    url = settings.URL_FORM
    # return redirect(url)
    output = {"url": url}
    return render(request, 'kakeibo/form.html', output)


@login_required
def form_shared(request):
    url = settings.URL_SHAREDFORM
    # return redirect(url)
    output = {"url": url}
    return render(request, 'kakeibo/form.html', output)


@login_required
@time_measure
def mine(request):
    # check year and month from GET parameter
    year, month = middleware.yearmonth(request)

    kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year)
    ekakeibos = kakeibos.exclude(Q(way='振替') | Q(way='収入') | Q(way="支出（クレジット）"))
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    expense = mylib.cal_sum_or_0(ekakeibos)

    # status, progress_bar
    pb_kakeibo, status_kakeibo = middleware.kakeibo_status(income, expense)

    # way
    ways_sum = kakeibos.values('way').annotate(Sum('fee'))
    ways = list()
    for w in ways_sum:
        if w['way'] != "振替":
            tmp = {"val": w['fee__sum'], "name": w['way']}
            ways.append(tmp)
    # saved
    rs = Resources.objects.get(name="SBI敬士")
    move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
    move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
    saved = move_to - move_from

    # resource
    resources = Resources.objects.all()

    # usage
    usages_chart = list()
    cash_usages = ekakeibos.values('usage').annotate(sum=Sum('fee')).order_by("sum").reverse()
    usage_names = {u.pk: u.name for u in Usages.objects.all()}
    for cu in cash_usages:
        name = usage_names[cu['usage']]
        val = cu['sum']
        usages_chart.append({"name": name, "val": val})

    # resources_year
    resources_year_chart, months_chart = middleware.resources_year_rev(12)
    logger.info(resources_year_chart)

    # kakeibo-usage
    usage_list = [u.name for u in Usages.objects.filter(is_expense=True)]
    kakeibo_usage = middleware.usage_kakeibo_table(usage_list)

    # Consolidated_usages: dict --> [(name, val),(name, val),(name, val),...]
    consolidated_usages_chart = sorted(middleware.consolidated_usages().items(), key=lambda x: -x[1])

    # total
    total = Resources.objects.all().aggregate(sum=Sum('current_val'))['sum']
    total_saved = rs.current_val + Resources.objects.get(name="貯金口座").current_val

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
    }
    return render(request, 'kakeibo/mine.html', output)


@login_required
@time_measure
def shared(request):
    # check year and month from GET parameter
    year, month = middleware.yearmonth(request)

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
    data_year = middleware.usage_shared_table(usage_list)

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
    return render(request, 'kakeibo/shared.html', output)


@login_required
@time_measure
def credit(request):
    # check year and month from GET parameter
    year, month = middleware.yearmonth(request)

    citems = CreditItems.objects.all()
    credits = Credits.objects.all()
    credits_month = credits.filter(debit_date__year=year, debit_date__month=month)

    res_credits = dict()
    sum_usage = dict()
    credits_sum = 0
    for citem in citems:
        credit = credits.filter(credit_item=citem).aggregate(Sum('fee'), Count('fee'), Avg('fee'))
        temp = dict()
        temp['name'] = citem.name
        if citem.usage:
            temp['usage'] = citem.usage.name
            tag = citem.usage.name
        else:
            temp['usage'] = ""
            tag = "その他"
        temp['sum'] = credit['fee__sum']
        credits_sum += credit['fee__sum']
        temp['avg'] = round(credit['fee__avg'])
        temp['count'] = credit['fee__count']
        if tag in sum_usage.keys():
            sum_usage[tag] = sum_usage[tag] + credit['fee__sum']
        else:
            sum_usage[tag] = credit['fee__sum']
        res_credits[citem.pk] = temp

    # credit_month
    res_month = list()
    credits_month_sum = 0
    for cm in credits_month:
        tmp = {
            "name": cm.credit_item.name,
            "val": cm.fee,
        }
        credits_month_sum += cm.fee
        res_month.append(tmp)

    # 支出項目の円表示
    res_sum_usage = dict()
    for k, v in sorted(sum_usage.items(), key=lambda x: -x[1]):
        res_sum_usage[k] = {"sum": v, "name": k}

    # Sumの降順に並び替え
    res_credits = sorted(res_credits.items(), key=lambda x: -x[1]['sum'])
    print(res_sum_usage)
    res_sum_usage = sorted(res_sum_usage.items(), key=lambda x: -x[1]['sum'])
    print(res_sum_usage)

    # count
    credits_month_count = credits_month.__len__()

    # return
    output = {
        "today": {"year": year, "month": month},
        "credits": res_credits,
        "sum_usage": res_sum_usage,
        "credits_sum": credits_sum,
        "credits_month": res_month,
        "credits_month_sum": credits_month_sum,
        "credits_month_count": credits_month_count,
    }

    return render(request, 'kakeibo/cdashboard.html', output)


@time_measure
def test(request):
    num=18
    # resource
    today = date.today()
    resources_chart = list()
    months = [(today + relativedelta(months=-i)) for i in range(num)]
    months_chart = [(str(m.year)+"/"+str(m.month)) for m in months]
    months_chart.reverse()

    for rs in Resources.objects.all():
        # kakeibo
        kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year)
        val = list()
        val.append(rs.current_val)
        ll = today
        print("=====")
        print(ll.month, ll.year)
        for i in range(1, num):
            move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
            val.append(val[i-1] - move_to + move_from)
            ll = ll + relativedelta(months=-1)
            logger.info(ll)
            print(ll.month, ll.year, move_from, move_to, kakeibos.__len__())
            kakeibos = Kakeibos.objects.filter(date__month=ll.month, date__year=ll.year)
        val.reverse()
        tmp = {"name": rs.name, "val": val,}
        resources_chart.append(tmp)

    output = {"resources_chart": resources_chart, "months_chart": months_chart}
    return render(request, 'kakeibo/test.html', output)


