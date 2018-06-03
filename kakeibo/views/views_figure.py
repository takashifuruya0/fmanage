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

# Create your views here.


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
    res = figure.fig_bars_basic_color(data=data, figtitle=figtitle, vbar_labels=vbar_labels, colors=colors, figsize=(10,10))
    return res


def bars_shared_eom(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "共通支出月末精算: " + year + "/" + month
    if year is None and month is None:
        return False
    budget = dict()
    payment = dict()
    sk = SharedKakeibos.objects.filter(date__year=year, date__month=month)
    budget['taka'] = 90000
    budget['hoko'] = 60000
    payment['taka'] = mylib.cal_sum_or_0(sk.filter(paid_by="敬士"))
    payment['hoko'] = mylib.cal_sum_or_0(sk.filter(paid_by="朋子"))
    inout = sum(budget.values()) - sum(payment.values())
    if inout <= 0:
        inout = -inout
        rb = [int(inout/2), 0, int(inout/2), 0]
        rb_name="赤字"
        seisan = [0, int(inout / 2) + budget['hoko'] - payment['hoko'], 0, 0]
    elif -inout + budget['hoko'] - payment['hoko'] >= 0:
        rb = [0, inout, 0, inout]
        rb_name = "黒字"
        seisan = [0, -inout + budget['hoko'] - payment['hoko'], 0, 0]
    else:
        rb = [0, inout/2, 0, inout/2]
        rb_name="黒字"
        seisan = [0, 0, 0, 0]
    data = {
        "現金精算": seisan,
        "予算": [budget['hoko'], 0, budget['taka'], 0],
        "支払": [0, payment['hoko'], 0, payment['taka']],
    }
    data[rb_name] = rb
    
    vbar_labels = ["朋子予算", "朋子支払", "敬士予算", "敬士支払"]
    res = figure.fig_bars_basic(data=data, figtitle=figtitle, vbar_labels=vbar_labels, figsize=(10, 10))
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
        if c.credit_item.usage in usage_list and c.credit_item.usage is not None:
            usage_sum[c.credit_item.usage.name] = usage_sum[c.credit_item.usage.name] + c.fee
        elif c.credit_item.usage is None:
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
        credit = Credits.objects.all()
    elif month is None:
        credit = Credits.objects.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        credit = Credits.objects.filter(date__year=year, date__month=month)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    credit_sum = dict()
    for ci in credititems:
        credit_sum[ci.name] = mylib.cal_sum_or_0(credit.filter(credit_item=ci))
    res = figure.fig_pie_basic(data=credit_sum, figtitle=figtitle, figsize=(12, 12), figid=3)
    return res


def pie_resource(request):
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "資産内訳"
    if year is None and month is None:
        kakeibos = Kakeibos.objects.all()
    elif month is None:
        kakeibos = Kakeibos.objects.filter(date__lt=date(int(year) + 1, 1, 1))
        figtitle = figtitle + "(" + str(year) + ")"
    else:
        kakeibos = Kakeibos.objects.filter(date__lt=date(int(year), int(month) + 1, 1))
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
        figsize = (12, 12)
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
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "資産内訳と先月比"
    if year is None or month is None:
        year = date.today().year
        month = date.today().month
    # 指定月の月末日を取得
    today = date(int(year), int(month) + 1, 1) - relativedelta(days=1)
    figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    # 指定月の一ヶ月前の月末日を取得
    last = date(int(year), int(month), 1) - relativedelta(days=1)
    # 範囲指定でレコード取得
    ka = Kakeibos.objects.filter(date__lte=today)
    kal = Kakeibos.objects.filter(date__year=today.year, date__month=today.month)
    # 計算
    for rs in resources:
        # left bar: this
        move_to = mylib.cal_sum_or_0(ka.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(ka.filter(move_from=rs))
        data[rs.name] = [rs.initial_val + move_to - move_from]
        # right bar: last
        move_to = mylib.cal_sum_or_0(kal.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(kal.filter(move_from=rs))
        data[rs.name].append(data[rs.name][0] - move_to + move_from)
    labels = [
        str(today.year) + "/" + str(today.month),
        str(last.year) + "/" + str(last.month),
    ]
    res = figure.fig_bars_basic(data=data,
                                figtitle=figtitle,
                                vbar_labels=labels,
                                figsize=(11, 11)
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
    figid = 200
    if year is None and month is None:
        kakeibos = ka.all()
    elif month is None:
        kakeibos = ka.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
        figid = figid + int(year)
    else:
        kakeibos = ka.filter(date__month=month, date__year=year)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
        figid = figid + int(year) + int(month)
    usages = Usages.objects.filter(is_expense=True)
    data = dict()
    for us in usages:
         data[us.name] = mylib.cal_sum_or_0(kakeibos.filter(usage=us))
    res = figure.fig_pie_basic(data=data, figtitle=figtitle, figid=figid)
    return res


def pie_usage(request):
    ka = Kakeibos.objects.filter(move_to=None)
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "支出内訳"
    figid = 250
    if year is None and month is None:
        kakeibos = ka.all()
    elif month is None:
        kakeibos = ka.filter(date__year=year)
        figtitle = figtitle + "(" + str(year) + ")"
        figid = figid + int(year)
    else:
        kakeibos = ka.filter(date__month=month, date__year=year)
        figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
        figid = figid + int(year) + int(month)
    usages = Usages.objects.filter(is_expense=True)
    data = dict()
    for us in usages:
         data[us.name] = mylib.cal_sum_or_0(kakeibos.filter(usage=us))
    res = figure.fig_pie_basic(data=data, figtitle=figtitle, figid=figid)
    return res


def test_figure(request):
    resources = Resources.objects.all()
    data = dict()
    year = request.GET.get(key="year")
    month = request.GET.get(key="month")
    figtitle = "資産内訳と先月比"
    if year is None or month is None:
        year = date.today().year
        month = date.today().month
    # 指定月の月末日を取得
    today = date(int(year), int(month) + 1, 1) - relativedelta(days=1)
    figtitle = figtitle + "(" + str(year) + "/" + str(month) + ")"
    # 指定月の一ヶ月前の月末日を取得
    last = date(int(year), int(month), 1) - relativedelta(days=1)
    # 範囲指定でレコード取得
    ka = Kakeibos.objects.filter(date__lte=today)
    kal = Kakeibos.objects.filter(date__year=today.year, date__month=today.month)
    # 計算
    for rs in resources:
        # left bar: this
        move_to = mylib.cal_sum_or_0(ka.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(ka.filter(move_from=rs))
        data[rs.name] = [rs.initial_val + move_to - move_from]
        # right bar: last
        move_to = mylib.cal_sum_or_0(kal.filter(move_to=rs))
        move_from = mylib.cal_sum_or_0(kal.filter(move_from=rs))
        data[rs.name].append(data[rs.name][0] - move_to + move_from)
    labels = [
        str(today.year) + "/" + str(today.month),
        str(last.year) + "/" + str(last.month),
    ]
    res = figure.fig_bars_basic(data=data,
                                figtitle=figtitle,
                                vbar_labels=labels,
                                figsize=(11, 11)
                                )
    return res
    return True
