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
from .functions import update_records, money, figure

# Create your views here.


@login_required
def dashboard(request):
    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = kakeibos.filter(way="収入") .aggregate(Sum('fee'))['fee__sum']
    salary = kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")) .aggregate(Sum('fee'))['fee__sum']
    expense = kakeibos.filter(way="支出（現金）") .aggregate(Sum('fee'))['fee__sum']
    debit = kakeibos.filter(way="引き落とし").aggregate(Sum('fee'))['fee__sum']
    shared_expense = kakeibos.filter(way="共通支出") .aggregate(Sum('fee'))['fee__sum']
    credit = kakeibos.filter(way="支出（クレジット）").aggregate(Sum('fee'))['fee__sum']
    smsg = "Hello, world"

    data = [expense, debit, shared]
    res = figure.fig_pie_basic(data=data, figtitle="test")
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
    smsg1, emsg1 = update_records.save_kakeibo_to_sql()
    smsg2, emsg2 = update_records.save_credit_to_sql()
    kakeibos = Kakeibos.objects.all()[:5]
    if smsg1 != "" and smsg2 != "":
        smsg = smsg1 + " and " + smsg2
    else:
        smsg = smsg1 + smsg2
    if emsg1 != "" and emsg2 != "":
        emsg = emsg1 + " and " + emsg2
    else:
        emsg = emsg1 + emsg2
    output = {
        "smsg": smsg,
        "emsg": emsg,
        "kakeibos": kakeibos,
    }
    return render(request, 'kakeibo/dashboard.html', output)


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
    income = kakeibos.filter(way="収入").aggregate(Sum('fee'))['fee__sum']
    salary = kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")).aggregate(Sum('fee'))['fee__sum']
    expense = kakeibos.filter(way="支出（現金）").aggregate(Sum('fee'))['fee__sum']
    debit = kakeibos.filter(way="引き落とし").aggregate(Sum('fee'))['fee__sum']
    shared_expense = kakeibos.filter(way="共通支出").aggregate(Sum('fee'))['fee__sum']
    credit = kakeibos.filter(way="支出（クレジット）").aggregate(Sum('fee'))['fee__sum']
    url = settings.URL_SHAREDFORM
    return redirect(url)


@login_required
def mine_month(request, year, month):
    kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year).order_by('date').reverse()
    income = kakeibos.filter(way="収入").aggregate(Sum('fee'))['fee__sum']
    salary = kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")).aggregate(Sum('fee'))['fee__sum']
    expense = kakeibos.filter(way="支出（現金）").aggregate(Sum('fee'))['fee__sum']
    debit = kakeibos.filter(way="引き落とし").aggregate(Sum('fee'))['fee__sum']
    shared_expense = kakeibos.filter(way="共通支出").aggregate(Sum('fee'))['fee__sum']
    credit = kakeibos.filter(way="支出（クレジット）").aggregate(Sum('fee'))['fee__sum']
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
            temp['usage'] = citem.usagename
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
    credits_sum = money.convert_yen(credits.aggregate(Sum('fee'))['fee__sum'])
    credits_month_sum = money.convert_yen(credits_month.aggregate(Sum('fee'))['fee__sum'])
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


def test(request):
    today = date.today()
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year).order_by('date').reverse()
    income = kakeibos.filter(way="収入").aggregate(Sum('fee'))['fee__sum']
    salary = kakeibos.filter(way="収入", usage=Usages.objects.get(name="給与")).aggregate(Sum('fee'))['fee__sum']
    expense = kakeibos.filter(way="支出（現金）").aggregate(Sum('fee'))['fee__sum']
    debit = kakeibos.filter(way="引き落とし").aggregate(Sum('fee'))['fee__sum']
    shared_expense = kakeibos.filter(way="共通支出").aggregate(Sum('fee'))['fee__sum']
    credit = kakeibos.filter(way="支出（クレジット）").aggregate(Sum('fee'))['fee__sum']

    data = {
        "現金支出": expense,
        "引き落とし": debit,
        "共通支出": shared_expense,
        "カード支出": credit,
    }
    res = figure.fig_pie_basic(data=data, figtitle="Breakdown of expenses")
    res = figure.fig_bars_basic()
    return res
