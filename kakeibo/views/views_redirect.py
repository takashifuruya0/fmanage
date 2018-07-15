# coding:utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings


@login_required
def redirect_knowledge(request):
    url = settings.URL_KNOWLEDGE
    return redirect(url)


@login_required
def redirect_metabase(request):
    url = settings.URL_METABASE
    return redirect(url)

