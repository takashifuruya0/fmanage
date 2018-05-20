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
from .models import *
# module
import requests, json
from datetime import datetime, date, timedelta
# function
from .functions import update_records, money, figure, mylib

# Create your views here.


@login_required
def dashboard(request):
    today = date.today()
    # kakeibo
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))
    # resource
    resources = Resources.objects.all()
    current_resource = dict()
    for rs in resources:
        move_to = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_from=rs))
        val = rs.initial_val + move_to - move_from
        if val is not 0:
            current_resource[rs.name] = money.convert_yen(val)
    # shared
    shared = SharedKakeibos.objects.filter(date__month=today.month, date__year=today.year)
    paidbyt = mylib.cal_sum_or_0(shared.filter(paid_by="敬士"))
    paidbyh = mylib.cal_sum_or_0(shared.filter(paid_by="朋子"))
    shared_usages = shared.values('usage').annotate(sum=Sum('fee'))
    if shared_usages.__len__() != 0:
        shared_grouped_by_usage = dict()
        for su in shared_usages:
            us = Usages.objects.get(pk=su['usage']).name
            shared_grouped_by_usage[us] = money.convert_yen(su['sum'])
    smsg = ""

    output = {
        "today": today,
        "smsg": smsg,
        "income": money.convert_yen(income),
        "expense": money.convert_yen(expense),
        "debit": money.convert_yen(debit),
        "shared_expense": money.convert_yen(shared_expense),
        "credit": money.convert_yen(credit),
        "current_resource": current_resource,
        "shared": money.convert_yen(paidbyh+paidbyt),
        "paidbyt": money.convert_yen(paidbyt),
        "paidbyh": money.convert_yen(paidbyh),
        "shared_grouped_by_usage": shared_grouped_by_usage,
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
    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    salary = mylib.cal_sum_or_0(kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")))
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))
    # resource
    resources = Resources.objects.all()
    current_resource = dict()
    for rs in resources:
        move_to = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_from=rs))
        val = rs.initial_val + move_to - move_from
        if val is not 0:
            current_resource[rs.name] = money.convert_yen(val)
    # usages
    usage_list = [i.pk for i in Usages.objects.all()]
    logger.info(usage_list)
    output = {
        "today": today,
        "income": money.convert_yen(income),
        "expense": money.convert_yen(expense),
        "debit": money.convert_yen(debit),
        "shared_expense": money.convert_yen(shared_expense),
        "credit": money.convert_yen(credit),
        "current_resource": current_resource,
        "usage_list": usage_list,
    }
    return render(request, 'kakeibo/mine.html', output)


@login_required
def mine_month(request, year, month):
    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    salary = mylib.cal_sum_or_0(kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")))
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))
    url = settings.URL_SHAREDFORM
    return redirect(url)


@login_required
def shared(request):
    today = date.today()
    skakeibos = SharedKakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    taka = skakeibos.filter(paid_by="敬士")
    hoko = skakeibos.filter(paid_by="朋子")
    url = settings.URL_SHAREDFORM
    return redirect(url)


@login_required
def shared_month(request, year, month):
    skakeibos = SharedKakeibos.objects.filter(date__month=month, date__year=year).order_by('date').reverse()
    taka = skakeibos.filter(paid_by="敬士")
    hoko = skakeibos.filter(paid_by="朋子")
    url = settings.URL_SHAREDFORM
    return redirect(url)


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


def bars_balance(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "収支内訳"
    if year is None and month is None:
        kakeibos = Kakeibos.objects.all()
    elif month is None:
        kakeibos = Kakeibos.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    salary = mylib.cal_sum_or_0(kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")))
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))

    data = {
        "支出（現金）": [0, expense],
        "引き落とし": [0, debit],
        "共通支出": [0, shared_expense],
        "支出（クレジット）": [0, credit],
        "収入": [income, 0],
    }
    colors = {
        "支出（現金）": "green",
        "引き落とし": "blue",
        "共通支出": "orange",
        "支出（クレジット）": "gray",
        "収入": "tomato",
    }
    vbar_labels = ['Income', 'Expense']
    res = figure.fig_bars_basic_color(data=data, figtitle=figtitle, vbar_labels=vbar_labels, colors=colors, figsize=(9, 9))
    return res


def pie_expense(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "支出内訳"
    if year is None and month is None:
        kakeibos = Kakeibos.objects.all()
    elif month is None:
        kakeibos = Kakeibos.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))

    data = {
        "Cash": expense,
        "Debit": debit,
        "Shared_expense": shared_expense,
        "Card": credit,
    }
    colors = {
        "Cash": "green",
        "Debit": "blue",
        "Shared_expense": "orange",
        "Card": "gray",
    }
    res = figure.fig_pie_basic_colored(data=data, figtitle=figtitle, colors=colors)
    return res


def pie_credititem(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "用途別クレジット内訳"
    if year is None and month is None:
        credits = Credits.objects.all()
    elif month is None:
        credits = Credits.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        credits = Credits.objects.filter(date__year=year, date__month=month)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    usage_list = list()
    usage_sum = dict()
    usage_sum["その他"] = 0
    for c in credits:
        if c.credit_item.usage in usage_list and c.credit_item.usage != None:
            usage_sum[c.credit_item.usage.name] = usage_sum[c.credit_item.usage.name] + c.fee
        elif c.credit_item.usage == None:
            usage_list.append("その他")
            usage_sum["その他"] = c.fee + usage_sum["その他"]
        else:
            usage_list.append(c.credit_item.usage)
            usage_sum[c.credit_item.usage.name] = c.fee

    res = figure.fig_pie_basic(data=usage_sum, figtitle=figtitle, figid=4)
    return res


def pie_credit(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "項目別クレジット内訳"
    credititems = CreditItems.objects.all()
    if year is None and month is None:
        credits = Credits.objects.all()
    elif month is None:
        credits = Credits.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        credits = Credits.objects.filter(date__year=year, date__month=month)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    credit_sum = dict()
    for ci in credititems:
        credit_sum[ci.name] = mylib.cal_sum_or_0(credits.filter(credit_item=ci))
    res = figure.fig_pie_basic(data=credit_sum, figtitle=figtitle, figsize=(12, 12), figid=3)
    return res


def pie_resource(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "資産内訳"
    if year is None and month is None:
        kakeibos = Kakeibos.objects.all()
    elif month is None:
        kakeibos = Kakeibos.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        kakeibos = Kakeibos.objects.filter(date__year=year, date__month=month)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    resources = Resources.objects.all()
    data = dict()
    for rs in resources:
        move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from=rs))
        data[rs.name] = rs.initial_val + move_to - move_from
    res = figure.fig_pie_basic(data=data, figtitle=figtitle,  figid=10, threshold=0)
    return res


def pie_shared(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "共通支出内訳"
    if year is None and month is None:
        shared = SharedKakeibos.objects.all()
        figid = 15
    elif month is None:
        shared = SharedKakeibos.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
        figid = int(year) + 15
    else:
        shared = SharedKakeibos.objects.filter(date__year=year, date__month=month)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
        figid = int(year) + int(month) + 15
    usages = Usages.objects.filter(is_expense=True)
    data = dict()
    for us in usages:
        data[us.name] = mylib.cal_sum_or_0(shared.filter(usage=us))
    res = figure.fig_pie_basic(data=data, figtitle=figtitle,  figid=figid, threshold=5, )
    return res


def barline_usage(request):
    id = request.GET.get("usageid")
    figid = 100 + int(id)
    us = Usages.objects.get(pk=id)
    label = us.name
    height = list()
    height_sum = list()
    xticklabel = list()
    for j in range(2017, 2019):
        for i in range(4, 13):
            ka = Kakeibos.objects.filter(date__year=j, date__month=i)
            if ka.__len__() is 0:
                break
            else:
                ka = ka.filter(usage=us)
                height.append(mylib.cal_sum_or_0(ka))
                height_sum.append(sum(height))
                xticklabel.append(str(j - 2000) + "/" + str(i))
    xlim = [i for i in range(0, len(height))]
    ylim = [i for i in range(0, max(height_sum), 100000)]
    yticklabel = [money.convert_yen(i) for i in ylim]
    res = figure.fig_barline_basic(height_bar=height, left_bar=xlim, label_bar=label,
                                   height_line=height_sum, left_line=xlim, label_line="cumulative",
                                   ylim=ylim, yticklabel=yticklabel, xlim=xlim, xticklabel=xticklabel,
                                   figsize=(10, 10), figid=figid)
    return res


def barline_expense_cash(request):
    year = request.GET.get("year")
    month = request.GET.get("month")
    rs = Resources.objects.get(name="財布")
    kakeibos = Kakeibos.objects.filter(move_from=rs)
    height = list()
    left = list()
    height_sum = list()
    xlim = list()
    xticklabel = list()
    if year is not None and month is not None:
        kakeibos = kakeibos.filter(date__year=year, date__month=month)
        figtitle = "現金支出推移 (" + str(year) + "/" + str(month) + ")"
        ylim = [i for i in range(0, 130000, 10000)]
        figsize = (10, 10)
        figid = 100 + int(year) + int(month)
        for j in range(1, 32):
            ka = kakeibos.filter(date__day=j)
            left.append(j)
            height.append(mylib.cal_sum_or_0(ka))
            height_sum.append(sum(height))
    elif year is not None:
        kakeibos = kakeibos.filter(date__year=year)
        figtitle = "現金支出推移 (" + str(year) + ")"
        ylim = [i for i in range(0, 1200000, 200000)]
        figsize = (11, 11)
        figid = 100 + int(year)
        for j in range(1, 13):
            ka = kakeibos.filter(date__month=j)
            left.append(j)
            height.append(mylib.cal_sum_or_0(ka))
            height_sum.append(sum(height))
    else:
        dates = [ka.date for ka in kakeibos]
        mindate = min(dates)
        maxdate = max(dates)
        figtitle = "現金支出推移"
        ylim = [i for i in range(0, 3000000, 500000)]
        figsize = (12, 12)
        figid = 100
        tmp = 0
        while mindate < maxdate:
            ka = kakeibos.filter(date__year=mindate.year, date__month=mindate.month)
            left.append(tmp)
            height.append(mylib.cal_sum_or_0(ka))
            height_sum.append(sum(height))
            mindate += relativedelta(months=1)
            xlim.append(tmp)
            xticklabel.append(str(mindate.year-2000)+"/"+str(mindate.month))
            tmp += 1
    yticklabel = [money.convert_yen(i) for i in ylim]
    label_line = "支出累計 (" + money.convert_yen(sum(height)) + ")"
    res = figure.fig_barline_basic(height_bar=height, left_bar=left, label_bar="現金支出",
                                   height_line=height_sum, left_line=left, label_line=label_line,
                                   xlim=xlim, xticklabel=xticklabel, ylim=ylim, yticklabel=yticklabel,
                                   figtitle=figtitle, figsize=figsize, figid=figid)
    return res


def bars_resource(request):
    resources = Resources.objects.all()
    data = dict()
    today = date.today()
    last = today - relativedelta(months=1)
    ka = Kakeibos.objects.all()
    kal = ka.exclude(date__month=today.month, date__year=today.year)
    for rs in resources:
        move_to = mylib.cal_sum_or_0(ka.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(ka.filter(move_from=rs))
        data[rs.name] = [rs.initial_val + move_to - move_from]
        move_to = mylib.cal_sum_or_0(kal.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(kal.filter(move_from=rs))
        data[rs.name].append(rs.initial_val + move_to - move_from)
    labels = [
        str(today.year) + "/" + str(today.month),
        str(last.year) + "/" + str(last.month),
              ]
    res = figure.fig_bars_basic(data=data,
                                figtitle="資産内訳と先月比",
                                vbar_labels=labels,
                                figsize=(10, 10)
                                )
    return res


def lines_usage_cash(request):
    ka = Kakeibos.objects.filter(move_from=Resources.objects.get(name="財布"))
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "現金支出内訳"
    if year is None and month is None:
        kakeibos = ka.all()
    elif month is None:
        kakeibos = ka.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        kakeibos = ka.filter(date__month=month, date__year=year)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    left = list()
    usages = [i for i in Usages.objects.filter(is_expense=True)]
    height = [list() for i in usages]
    colors = [i.color for i in usages]
    for i in range(1, 32):
        ka = kakeibos.filter(date__day=i)
        left.append(i)
        tmp = 0
        for us in usages:
            height[tmp].append(mylib.cal_sum_or_0(ka.filter(usage=us)))
            tmp += 1

    heights = [i for i in height]
    lefts = [left for i in height]
    labels = [i.name for i in usages]
    res = figure.fig_lines_basic(heights=heights, lefts=lefts, colors=colors,
                                 labels=labels, figtitle=figtitle, figsize=(11, 11)
                                 )
    return res


def pie_usage_cash(request):
    ka = Kakeibos.objects.filter(move_from=Resources.objects.get(name="財布"))
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "現金支出内訳"
    if year is None and month is None:
        kakeibos = ka.all()
    elif month is None:
        kakeibos = ka.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        kakeibos = ka.filter(date__month=month, date__year=year)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    usages = Usages.objects.filter(is_expense=True)
    data = dict()
    for us in usages:
         data[us.name] = mylib.cal_sum_or_0(kakeibos.filter(usage=us))
    res = figure.fig_pie_basic(data=data, figtitle=figtitle)
    return res


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


class KakeiboList(ListView):
    model = Kakeibos
    ordering = ['-date']
    paginate_by = 20
    queryset = Kakeibos.objects.exclude(way="振替")  # Default: Model.objects.all()


class SharedList(ListView):
    model = SharedKakeibos
    ordering = ['-date']
    paginate_by = 20
