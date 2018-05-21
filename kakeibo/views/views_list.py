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
class KakeiboList(ListView):
    model = Kakeibos
    ordering = ['-date']
    paginate_by = 20
    queryset = Kakeibos.objects.exclude(way="振替")  # Default: Model.objects.all()


class SharedList(ListView):
    model = SharedKakeibos
    ordering = ['-date']
    paginate_by = 20
