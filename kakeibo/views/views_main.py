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
# budget
budget_t = 90000
budget_h = 60000
budget_shared = budget_t + budget_h

# Create your views here.


@login_required
def dashboard(request):
    today = date.today()
    # kakeibo
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year)
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    expense = mylib.cal_sum_or_0(kakeibos.exclude(Q(way='振替') | Q(way='収入') | Q(way="支出（クレジット）")))
    # status, progress_bar
    if income > expense:
        status_kakeibo = "primary"
        pb_kakeibo = {"in": 100, "out": int(expense / income * 100)}
    else:
        status_kakeibo = "danger"
        pb_kakeibo = {"in": int(income / expense * 100), "out": 100}
    # way
    ways_sum = kakeibos.values('way').annotate(Sum('fee'))
    current_way = dict()
    for w in ways_sum:
        current_way[w['way']] = money.convert_yen(w['fee__sum'])
    current_way.pop("振替")
    # resource
    current_resource = dict()
    for rs in Resources.objects.all():
        # current_valがあれば早い
        if rs.current_val is not None:
            val = rs.current_val
        else:
            move_to = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_from=rs))
            val = rs.initial_val + move_to - move_from
            logger.info(rs.name+":"+str(val))
        if val is not 0:
            current_resource[rs.name] = money.convert_yen(val)
    # shared
    shared = SharedKakeibos.objects.filter(date__month=today.month, date__year=today.year)
    paidbyt = mylib.cal_sum_or_0(shared.filter(paid_by="敬士"))
    paidbyh = mylib.cal_sum_or_0(shared.filter(paid_by="朋子"))
    inout_shared = budget_shared - paidbyt - paidbyh
    shared_usages = shared.values('usage').annotate(sum=Sum('fee'))
    # shared_grouped_by_usage
    shared_grouped_by_usage = dict()
    if shared_usages.__len__() != 0:
        for su in shared_usages:
            us = Usages.objects.get(pk=su['usage']).name
            shared_grouped_by_usage[us] = money.convert_yen(su['sum'])
    # End of Month
    # 赤字→精算あり
    if inout_shared <= 0:
        move = budget_h - inout_shared/2 - paidbyh
        status_shared = "danger"
        pb_shared = {"in": int(budget_shared / (paidbyh + paidbyt) * 100), "out": 100}
    # 黒字＋朋子さん支払いが朋子さん予算以下→精算あり
    elif -inout_shared + budget_h - paidbyh >= 0:
        move = budget_h - inout_shared - paidbyh
        status_shared = "primary"
        pb_shared = {"in": 100, "out": int((paidbyh + paidbyt) / budget_shared * 100)}
    # 黒字＋朋子さん支払い＜朋子さん予算→精算なし
    else:
        move = 0
        status_shared = "primary"
        pb_shared = {"in": 100, "out": int((paidbyh + paidbyt) / budget_shared * 100)}
    # msg
    smsg = ""

    output = {
        "today": today,
        "smsg": smsg,
        # kakeibo
        "inout": money.convert_yen(income-expense),
        "income": money.convert_yen(income),
        "expense": money.convert_yen(expense),
        "current_way": current_way,
        "current_resource": current_resource,
        # shared
        "inout_shared": money.convert_yen(inout_shared),
        "budget_shared": money.convert_yen(budget_shared),
        "expense_shared": money.convert_yen(paidbyh + paidbyt),
        "move": money.convert_yen(move),
        "shared_grouped_by_usage": shared_grouped_by_usage,
        "paidby": {"t": money.convert_yen(paidbyt), "h": money.convert_yen(paidbyh)},
        # progress bar and status
        "pb_kakeibo": pb_kakeibo,
        "pb_shared": pb_shared,
        "status": {"kakeibo": status_kakeibo, "shared": status_shared},
    }
    logger.info("output: " + str(output))
    return render(request, 'kakeibo/dashboard.html', output)


@login_required
def updates(request):
    smsg = ["", "", ""]
    emsg = ["", "", ""]
    smsg[0], emsg[0] = update_records.init_resources_usages()
    smsg[1], emsg[1] = update_records.save_kakeibo_to_sql()
    smsg[2], emsg[2] = update_records.save_credit_to_sql()
    for i in range(smsg.__len__()):
        if smsg[i] != "":
            logger.info(smsg[i])
        if emsg[i] != "":
            logger.error(emsg[i])
    return redirect('kakeibo:dashboard')


@login_required
def updates_shared(request):
    smsg, emsg = update_records.save_shared_to_sql()
    if smsg != "":
        logger.info(smsg)
    if emsg != "":
        logger.error(emsg)
    return redirect('kakeibo:dashboard')


@login_required
def redirect_form(request):
    url = settings.URL_FORM
    return redirect(url)


@login_required
def redirect_sharedform(request):
    url = settings.URL_SHAREDFORM
    return redirect(url)


@login_required
def mine(request):
    if request.GET.get(key="yearmonth") is not None:
        year = request.GET.get(key="yearmonth")[0:4]
        month = request.GET.get(key="yearmonth")[5:]
    else:
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
    if year is None or month is None:
        year = date.today().year
        month = date.today().month

    kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year)
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    expense = mylib.cal_sum_or_0(kakeibos.exclude(Q(way='振替') | Q(way='収入') | Q(way="支出（クレジット）")))
    # status, progress_bar
    if income > expense:
        status = "primary"
        pb_kakeibo_in = 100
        pb_kakeibo_out = int(expense / income * 100)
    else:
        status = "danger"
        pb_kakeibo_in = int(income / expense * 100)
        pb_kakeibo_out = 100
    pb_kakeibo = {"in": pb_kakeibo_in, "out": pb_kakeibo_out}
    # way
    ways_sum = kakeibos.values('way').annotate(Sum('fee'))
    current_way = dict()
    for w in ways_sum:
        if w['way'] != "振替":
            current_way[w['way']] = money.convert_yen(w['fee__sum'])
    # resource
    current_resource = dict()
    for rs in Resources.objects.all():
        # current_valがあれば早い
        if rs.current_val is not None:
            val = rs.current_val
        else:
            move_to = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_from=rs))
            val = rs.initial_val + move_to - move_from
            logger.info(rs.name + ":" + str(val))
        if val is not 0:
            current_resource[rs.name] = money.convert_yen(val)
    # usage
    usages = Usages.objects.all()
    current_usage = dict()
    for us in usages:
        val = mylib.cal_sum_or_0(kakeibos.filter(usage=us))
        if val is not 0 and us.is_expense:
            current_usage[us.name] = money.convert_yen(val)
    # saved
    rs = Resources.objects.get(name="SBI敬士")
    move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
    move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
    saved = move_to - move_from

    # output
    output = {
        "today": {"year": year, "month": month},
        # status
        "status": status,
        "saved": money.convert_yen(saved),
        "inout": money.convert_yen(income - expense),
        # progress_bar
        "pb_kakeibo": pb_kakeibo,
        "income": money.convert_yen(income),
        "expense": money.convert_yen(expense),
        # current list
        "current_resource": current_resource,
        "current_usage": current_usage,
        "current_way": current_way,
    }
    return render(request, 'kakeibo/mine.html', output)


@login_required
def shared(request):
    if request.GET.get(key="yearmonth") is not None:
        year = request.GET.get(key="yearmonth")[0:4]
        month = request.GET.get(key="yearmonth")[5:]
    else:
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
    if year is None or month is None:
        year = date.today().year
        month = date.today().month

    # data
    skakeibos_year = SharedKakeibos.objects.filter(date__year=year)
    skakeibos = skakeibos_year.filter(date__month=month)
    paidbyt = mylib.cal_sum_or_0(skakeibos.filter(paid_by="敬士"))
    paidbyh = mylib.cal_sum_or_0(skakeibos.filter(paid_by="朋子"))

    # inout
    expense = mylib.cal_sum_or_0(skakeibos)
    budget = budget_h + budget_t
    inout_shared = budget - expense

    # shared_grouped_by_usage
    shared_usages = skakeibos.values('usage').annotate(sum=Sum('fee'))
    shared_grouped_by_usage = dict()
    if shared_usages.__len__() != 0:
        for su in shared_usages:
            us = Usages.objects.get(pk=su['usage']).name
            shared_grouped_by_usage[us] = money.convert_yen(su['sum'])

    # End of Month
    # 赤字→精算あり
    if inout_shared <= 0:
        move = budget_h - inout_shared / 2 - paidbyh
        status_shared = "danger"
        pb_shared_in = int(budget_shared / expense * 100)
        pb_shared_out = 100
    # 黒字
    else:
        status_shared = "primary"
        pb_shared_in = 100
        pb_shared_out = int(expense / budget * 100)
        # 朋子さん支払いが朋子さん予算以下→精算あり
        if -inout_shared + budget_h - paidbyh >= 0:
            move = budget_h - inout_shared - paidbyh
        # 朋子さん支払い＜朋子さん予算→精算なし
        else:
            move = 0

    # 年間
    data_year = list()
    usage_list = ["家賃", "食費", "日常消耗品", "ガス", "電気", "水道", "その他"]
    logger.info("usage_list:" + str(usage_list))
    for i in range(1, 13):
        data_tmp = dict()
        sk = skakeibos_year.filter(date__month=i)
        if sk.__len__() is not 0:
            data_tmp["month"] = i
            data_tmp2 = list()
            sus = sk.values('usage').annotate(sum=Sum('fee'))
            for j in usage_list:
                for su in sus:
                    tmp = "-"
                    if Usages.objects.get(pk=su['usage']).name == j:
                        tmp = money.convert_yen(su['sum'])
                        break
                data_tmp2.append(tmp)
            val_tmp = mylib.cal_sum_or_0(sk)
            data_tmp["sum"] = money.convert_yen(val_tmp)
            data_tmp["percent"] = val_tmp / (budget + 30000) * 100
            if val_tmp < budget:
                data_tmp["color"] = "success"
            else:
                data_tmp["color"] = "danger"
            data_tmp["data"] = data_tmp2
            data_year.append(data_tmp)
    usage_list.insert(0, "合計")

    logger.info("data_year"+str(data_year))
    # output
    output = {
        "today": {"year": year, "month": month},
        # status
        "status": status_shared,
        # progress_bar
        "pb_shared": {"in": pb_shared_in, "out": pb_shared_out},
        # data
        "budget": money.convert_yen(budget),
        "expense": money.convert_yen(expense),
        "paidby": {"t": money.convert_yen(paidbyt), "h": money.convert_yen(paidbyh)},
        "inout": money.convert_yen(budget - expense),
        "move": money.convert_yen(move),
        "shared_grouped_by_usage": shared_grouped_by_usage,
        #table
        "data_year": data_year,
        "usage_list": usage_list,
    }
    return render(request, 'kakeibo/shared.html', output)


@login_required
def credit(request):
    today = date.today()
    citems = CreditItems.objects.all()
    credits = Credits.objects.all().order_by("-date")
    credits_month = credits.filter(debit_date__month=today.month, debit_date__year=today.year)

    res_credits = dict()
    sum_usage = dict()
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
        temp['sort'] = credit['fee__sum']
        temp['sum'] = money.convert_yen(credit['fee__sum'])
        temp['avg'] = money.convert_yen(round(credit['fee__avg']))
        temp['count'] = credit['fee__count']
        if tag in sum_usage.keys():
            sum_usage[tag] = sum_usage[tag] + credit['fee__sum']
        else:
            sum_usage[tag] = credit['fee__sum']
        res_credits[citem.pk] = temp

    # Sumの降順に並び替え
    res_credits = sorted(res_credits.items(), key=lambda x: -x[1]['sort'])
    # 支出項目の円表示
    res_sum_usage = dict()
    for k, v in sorted(sum_usage.items(), key=lambda x: -x[1]):
        res_sum_usage[k] = money.convert_yen(v)
    # クレジット支出一覧から5レコード
    credit_list = credits[:5]
    # Sum
    credits_sum = money.convert_yen(mylib.cal_sum_or_0(credits))
    credits_month_sum = money.convert_yen(mylib.cal_sum_or_0(credits_month))
    credits_month_count = credits_month.aggregate(Count('fee'))['fee__count']
    # return
    output = {
        "today": today,
        "credits": res_credits,
        "sum_usage": res_sum_usage,
        "credit_list": credit_list,
        "credits_sum": credits_sum,
        "credits_month_sum": credits_month_sum,
        "credits_month_count": credits_month_count,
    }

    return render(request, 'kakeibo/cdashboard.html', output)


def test(request):
    today = date.today()
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    rs = Resources.objects.get(name=request.GET.get(key="resource"))
    figtitle = "Usage-Breakdown @" + rs.name
    if year is None:
        kakeibos = Kakeibos.objects.filter(move_from=rs)
    elif month is None:
        kakeibos = Kakeibos.objects.filter(date__year=year, move_from=rs)
        figtitle = figtitle + "(CY" + str(year) + ")"
    else:
        kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year, move_from=rs)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    usages = Usages.objects.filter(is_expense=True)
    data = dict()
    for us in usages:
        data[us.name] = mylib.cal_sum_or_0(kakeibos.filter(usage=us))

    res = figure.fig_pie_basic(data=data, figtitle=figtitle)
    return res
    return True

