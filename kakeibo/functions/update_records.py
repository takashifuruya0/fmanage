# coding:utf-8

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count, Q
from django.db import transaction
from django.conf import settings
# model
from kakeibo.models import Kakeibos, Usages, Resources, Credits, CreditItems, Cards, SharedKakeibos

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
                    kakeibo = Kakeibos()
                    kakeibo.date = parser.parse(val['タイムスタンプ']).astimezone(timezone('Asia/Tokyo'))
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
        emsg = "Updating kakeibo-records failed: " + str(e)
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
                credit.date = parser.parse(v['タイムスタンプ']).astimezone(timezone('Asia/Tokyo'))
                credit.fee = v['fee']
                debit_year = "20" + v['debit_date'][0:2]
                debit_month = v['debit_date'][3:5]
                credit.debit_date = debit_year+"-"+debit_month+"-01"
                credit.save()
            smsg = "Updating kakeibo-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating credit-records failed: " + str(e)
    # Dashboardへリダイレクト
    return smsg, emsg


def init_resources_usages():
    try:
        if len(Resources.objects.all()) == 0:
            Resources(**{'date': date(2017, 1, 1), 'initial_val': 439386, 'name': 'ゆうちょ', 'color': None}).save()
            Resources(**{'date': date(2018, 1, 1), 'initial_val': 841390, 'name': 'SBI敬士', 'color': None}).save()
            Resources(**{'date': date(2018, 1, 1), 'initial_val': 22881, 'name': '財布', 'color': None}).save()
            Resources(**{'date': date(2018, 1, 1), 'initial_val': 60000, 'name': '共通口座', 'color': None}).save()
            Resources(**{'date': date(2018, 1, 1), 'initial_val': 86200, 'name': '貯金口座', 'color': None}).save()
            Resources(**{'date': date(2018, 4, 23), 'initial_val': 0, 'name': '朋子口座', 'color': None}).save()

        if len(Usages.objects.all()) == 0:
            Usages(**{'date': date(2018, 1, 1), 'name': '給与', 'is_expense': False, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'SBI朋子', 'is_expense': False, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'その他収入', 'is_expense': False, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '食費', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '外食費', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '交際費', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '日常消耗品', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '散髪・衣服', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '交通費', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '喫茶店', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '娯楽費', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'コンビニ', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '書籍', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'クレジット（個人）', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'クレジット（家族）', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '電気', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'ガス', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '水道', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'NHK', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '家賃', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '奨学金返還', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': 'その他', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '共通支出', 'is_expense': True, 'color': None}).save()

        smsg = "Successfully initialize resources and usages. "
        emsg = ""

    except Exception as e:
        smsg = ""
        emsg = "Failed to initialize resources and usages: " + str(e)

    finally:
        return smsg, emsg


def save_shared_to_sql():
    try:
        # transaction starts
        with transaction.atomic():
            # 初期化
            SharedKakeibos.objects.all().delete()
            # SSから取得
            url = settings.URL_SHARED
            r = requests.get(url)
            data = r.json()
            for k, val in data.items():
                if val['金額'] is not 0:
                    kakeibo = SharedKakeibos()
                    kakeibo.date = parser.parse(val['タイムスタンプ']).astimezone(timezone('Asia/Tokyo'))
                    kakeibo.fee = (val['金額'])
                    kakeibo.way = val['項目']
                    kakeibo.memo = val['メモ']
                    kakeibo.paid_by = val['支払者']
                    kakeibo.is_settled = False
                    if kakeibo.way == "引き落とし":
                        kakeibo.move_from = Resources.objects.get(name=val['引き落とし対象'])
                        kakeibo.usage = Usages.objects.get(name=val['引き落とし項目'])
                    elif kakeibo.way == "現金":
                        kakeibo.move_from = Resources.objects.get(name='財布')
                        kakeibo.usage = Usages.objects.get(name=val['支出項目'])
                    elif kakeibo.way == "クレジット":
                        kakeibo.usage = Usages.objects.get(name=val['支出項目'])
                    # save
                    kakeibo.save()
            smsg = "Updating shared-kakeibo-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating shared-kakeibo-records failed: " + str(e)
        print(e)
    return smsg, emsg
