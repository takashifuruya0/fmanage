# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.db.models import Avg, Sum, Count, Q
from django.db import transaction
# model
from .models import *
# module
import requests, json
from datetime import datetime, date
# function
from .functions import update_records, money, figure, mylib

# Create your views here.


@login_required
def dashboard(request):

    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    salary = mylib.cal_sum_or_0(kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")))
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))

    smsg = "Hello, world"

    data = {
         "現金支出": expense, 
         "引き落とし": debit, 
         "共通支出": shared_expense,
    }
    output = {
        "smsg": smsg,
        "income": money.convert_yen(income),
        "expense": money.convert_yen(expense),
        "debit": money.convert_yen(debit),
        "shared_expense": money.convert_yen(shared_expense),
        "credit": money.convert_yen(credit),
        "salary": money.convert_yen(salary),
        "kakeibos": kakeibos[:5],
    }
    return render(request, 'kakeibo/dashboard.html', output)


@login_required
def updates(request):
    smsg0, emsg0 = update_records.init_resources_usages()
    smsg1, emsg1 = update_records.save_kakeibo_to_sql()
    smsg2, emsg2 = update_records.save_credit_to_sql()
    smsg = smsg0 + "/" + smsg1 + "/" + smsg2
    emsg = emsg0 + "/" + emsg1 + "/" + emsg2
    return redirect('kakeibo:dashboard')


@login_required
def updates_shared(request):
    smsg0, emsg0 = update_records.save_shared_to_sql()
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
    url = settings.URL_SHAREDFORM
    return redirect(url)


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
        "credits": res_credits,
        "sum_usage": res_sum_usage,
        "credit_list": credit_list,
        "credits_sum": credits_sum,
        "credits_month_sum": credits_month_sum,
        "credits_month_count": credits_month_count,
    }

    return render(request, 'kakeibo/cdashboard.html', output)


def bars_balance(request):
    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = mylib.cal_sum_or_0(kakeibos.filter(way="収入"))
    salary = mylib.cal_sum_or_0(kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")))
    expense = mylib.cal_sum_or_0(kakeibos.filter(way="支出（現金）"))
    debit = mylib.cal_sum_or_0(kakeibos.filter(way="引き落とし"))
    shared_expense = mylib.cal_sum_or_0(kakeibos.filter(way="共通支出"))
    credit = mylib.cal_sum_or_0(kakeibos.filter(way="支出（クレジット）"))

    data = {
        "Cash": [0, expense],
        "Debit": [0, debit],
        "Shared_expense": [0, shared_expense],
        "Card": [0, credit],
        "Income": [income, 0],
    }
    colors = {
        "Cash": "green",
        "Debit": "blue",
        "Shared_expense": "orange",
        "Card": "gray",
        "Income": "tomato",
    }
    vbar_labels = ['Income', 'Expense']
    res = figure.fig_bars_basic_color(data=data, figtitle="Balance", vbar_labels=vbar_labels, colors=colors)
    return res


def pie_expense(request):
    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
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
    res = figure.fig_pie_basic_colored(data=data, figtitle="Breakdown of expenses", colors=colors)
    return res


def pie_credit(request):
    credits = Credits.objects.all()
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

    res = figure.fig_pie_basic(data=usage_sum, figtitle="Usage of credit")
    return res


def test(reqest):
    return True
