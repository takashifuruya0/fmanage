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
from .functions import update_records, money

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
