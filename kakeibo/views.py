# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count, Q
from django.db import transaction

# model
from .models import *

# module
import requests
import json
from datetime import datetime, date


# Create your views here.


def dashboard(request):
    kakeibos = Kakeibos.objects.all()[:5]
    output = {
        "kakeibos": kakeibos,
    }
    return render(request, 'dashboard.html', output)
