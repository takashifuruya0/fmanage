# coding:utf-8

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count, Q
from django.db import transaction
from django.conf import settings
# model
from kakeibo.models import Kakeibos, Usages, Resources, Credits, CreditItems, Cards

# module
import json, requests
from datetime import datetime, date
from bs4 import BeautifulSoup
from pytz import timezone
from dateutil import parser


def save_kakeibo_to_sql():
    try:
        # transaction starts
        with transaction.atomic():
            # 初期化
            Kakeibos.objects.all().delete()
            # SSから取得
            url = settings.URL_KAKEIBO
            r = requests.get(url+"?method=kakeibo")
            data = r.json()
            for k, val in data.items():
                if val['金額'] is not 0:
                    print(val)
                    kakeibo = Kakeibos()
                    kakeibo.date = val['タイムスタンプ'][0:10]
                    kakeibo.fee = (val['金額'])
                    kakeibo.way = val['項目']
                    kakeibo.memo = val['メモ']
                    kakeibo.tag = val['タグ']
                    if kakeibo.way == "引き落とし":
                        kakeibo.move_from = Resources.objects.get(name=val['引き落とし対象'])
                        kakeibo.usage = Usages.objects.get(name=val['引き落とし項目'])
                    elif kakeibo.way == "振替":
                        kakeibo.move_from = Resources.objects.get(name=val['From'])
                        kakeibo.move_to = Resources.objects.get(name=val['To'])
                    elif kakeibo.way == "収入":
                        kakeibo.move_to = Resources.objects.get(name=val['振込先'])
                        if val['収入源'] == 'その他':
                            val['収入源'] = 'その他収入'
                        kakeibo.usage = Usages.objects.get(name=val['収入源'])
                    elif kakeibo.way == "支出（現金）":
                        kakeibo.move_from = Resources.objects.get(name='財布')
                        kakeibo.usage = Usages.objects.get(name=val['支出項目'])
                    elif kakeibo.way == "支出（クレジット）":
                        kakeibo.usage = Usages.objects.get(name=val['支出項目'])
                    elif kakeibo.way == "共通支出":
                        kakeibo.usage = Usages.objects.get(name="共通支出")
                    # save
                    kakeibo.save()
            smsg = "Updating kakeibo-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating kakeibo @ecords failed: " + str(e)
    return smsg, emsg


def save_credit_to_sql():
    try:
        # transaction starts
        with transaction.atomic():
            # 初期化
            Credits.objects.all().delete()
            # GASのAPI
            url = settings.URL_KAKEIBO
            r = requests.get(url+"?method=credit")
            data = r.json()
            # 登録
            for k, v in data.items():
                credit = Credits()
                credititems = CreditItems.objects.filter(name=v['name'])
                if credititems.__len__() is 0:
                    new_item = CreditItems()
                    new_item.name = v['name']
                    new_item.date = v['date'][0:10]
                    new_item.save()
                    credit.credit_item = new_item
                else:
                    credit.credit_item = CreditItems.objects.get(name=v['name'])
                credit.date = v['date'][0:10]
                credit.fee = v['fee']
                debit_year = "20" + v['debit_date'][0:2]
                debit_month = v['debit_date'][3:5]
                credit.debit_date = debit_year+"-"+debit_month+"-01"
                credit.save()
            smsg = "Updating kakeibo-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating kakeibo @ecords failed: " + str(e)
    # Dashboardへリダイレクト
    return smsg, emsg
