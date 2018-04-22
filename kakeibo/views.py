# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count, Q
from django.db import transaction
# model
from .models import *
# module
import requests, json
from datetime import datetime, date
# function
from .functions import update_records

# Create your views here.


@login_required
def dashboard(request):
    kakeibos = Kakeibos.objects.all()[:5]
    smsg = "Hello, world"
    output = {
        "smsg": smsg,
        "kakeibos": kakeibos,
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