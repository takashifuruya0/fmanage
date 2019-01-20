# coding:utf-8
from django.db import transaction
from django.conf import settings
# model
from kakeibo.models import Kakeibos, Usages, Resources, Credits, CreditItems, Cards, SharedKakeibos
# module
import requests
from datetime import date
from pytz import timezone
from dateutil import parser
import logging
logger = logging.getLogger("django")


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
                        kakeibo.move_from = Resources.objects.get(name="財布")
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
                credit.date = parser.parse(v['date']).astimezone(timezone('Asia/Tokyo'))
                credit.fee = v['fee']
                debit_year = "20" + v['debit_date'][0:2]
                debit_month = v['debit_date'][3:5]
                credit.debit_date = debit_year+"-"+debit_month+"-01"
                credit.save()
            smsg = "Updating credit-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating credit-records failed: " + str(e)
    # Dashboardへリダイレクト
    return smsg, emsg


def init_resources_usages():
    try:
        if len(Resources.objects.all()) == 0:
            Resources(
                **{'date': date(2017, 1, 1), 'initial_val': 475928, 'name': 'ゆうちょ', 'color': None, 'is_saving': False}
            ).save()
            Resources(
                **{'date': date(2018, 1, 1), 'initial_val': 841390, 'name': 'SBI敬士', 'color': None, 'is_saving': True}
            ).save()
            Resources(
                **{'date': date(2018, 1, 1), 'initial_val': 44286, 'name': '財布', 'color': None, 'is_saving': False}
            ).save()
            Resources(
                **{'date': date(2018, 1, 1), 'initial_val': 60000, 'name': '共通口座', 'color': None, 'is_saving': False}
            ).save()
            Resources(
                **{'date': date(2018, 1, 1), 'initial_val': 85200, 'name': '貯金口座', 'color': None, 'is_saving': True}
            ).save()
            Resources(
                **{'date': date(2018, 4, 23), 'initial_val': 0, 'name': '朋子口座', 'color': None, 'is_saving': False}
            ).save()

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
            Usages(**{'date': date(2018, 1, 1), 'name': '仕事', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '自己啓発', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '通信費', 'is_expense': True, 'color': None}).save()
            Usages(**{'date': date(2018, 1, 1), 'name': '引越', 'is_expense': True, 'color': None}).save()

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
        emsg = "Updating shared-kakeibo-records failed: " + str(e) + ":" + str(val)
    return smsg, emsg


def consolidate_kakeibo():
    try:
        # transaction starts
        with transaction.atomic():

            # SSから取得
            url = "https://script.google.com/macros/s/AKfycbyszn8odB6D9bkL6H6fQJyA83PO3uske-I34F0bNhPsJeSlAN8/exec"
            r = requests.get(url+"?method=get_form&numdata=1000")
            data = r.json()
            for k, val in data.items():
                if val['金額'] is not 0:
                    # kakeibos.way = val['支払い方法']
                    # kakeibos.memo = val['メモ']
                    # kakeibos.tag = val['特別タグ']
                    # kakeibos.mail = val['家計簿メール']
                    # kakeibos.source = val['収入源']
                    # kakeibos.move_from = val['From(現金移動)']
                    # kakeibos.move_to = val['To(現金移動)']
                    # kakeibos.cash_or_credit = val['項目（現金・クレジット）']
                    # kakeibos.debit = val["項目（引き落とし）"]

                    # resourceの変換
                    if val['From(現金移動)'] == "SBI":
                        val['From(現金移動)'] = "SBI敬士"
                    elif val['From(現金移動)'] == "貯金":
                        val['From(現金移動)'] = "貯金口座"
                    if val['To(現金移動)'] == "SBI":
                        val['To(現金移動)'] = "SBI敬士"
                    elif val['To(現金移動)'] == "貯金":
                        val['To(現金移動)'] = "貯金口座"
                    # usageの変換
                    if val['項目（現金・クレジット）'] =="日用消耗品":
                        val['項目（現金・クレジット）'] = "日常消耗品"
                    elif val['項目（現金・クレジット）'] == "衣服・化粧品・散髪":
                        val['項目（現金・クレジット）'] = "散髪・衣服"
                    elif val['項目（現金・クレジット）'] == "本・漫画":
                        val['項目（現金・クレジット）'] = "書籍"
                    # 引き落としの変換
                    if val["項目（引き落とし）"] == "カード請求":
                        val["項目（引き落とし）"] = "クレジット（個人）"
                    elif val["項目（引き落とし）"] == "奨学金返済":
                        val["項目（引き落とし）"] = "奨学金返還"
                    # 収入源の変換
                    if val['収入源'] == "給与収入":
                        val['収入源'] = "給与"
                    # 支払い方法の変換
                    if val['支払い方法'] == "現金":
                        val['支払い方法'] = "支出（現金）"
                    elif val['支払い方法'] == "クレジットカード":
                        val['支払い方法'] = "支出（クレジット）"
                    elif val['支払い方法'] == "現金移動":
                        val['支払い方法'] = "振替"
                    # 登録
                    kakeibo = Kakeibos()
                    kakeibo.date = parser.parse(val['タイムスタンプ']).astimezone(timezone('Asia/Tokyo'))
                    kakeibo.fee = (val['金額'])
                    kakeibo.way = val['支払い方法']
                    kakeibo.memo = val['メモ']
                    if kakeibo.way == "引き落とし":
                        kakeibo.move_from = Resources.objects.get(name="ゆうちょ")
                        kakeibo.usage = Usages.objects.get(name=val['項目（引き落とし）'])
                    elif kakeibo.way == "振替":
                        kakeibo.move_from = Resources.objects.get(name=val['From(現金移動)'])
                        kakeibo.move_to = Resources.objects.get(name=val['To(現金移動)'])
                    elif kakeibo.way == "収入":
                        kakeibo.usage = Usages.objects.get(name=val['収入源'])
                        kakeibo.move_to = Resources.objects.get(name="ゆうちょ")
                    elif kakeibo.way == "支出（現金）":
                        kakeibo.move_from = Resources.objects.get(name='財布')
                        kakeibo.usage = Usages.objects.get(name=val['項目（現金・クレジット）'])
                    elif kakeibo.way == "支出（クレジット）":
                        kakeibo.usage = Usages.objects.get(name=val['項目（現金・クレジット）'])

                    # save
                    kakeibo.save()
            smsg = "Consolidating kakeibo-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Consolidating kakeibo-records failed: " + str(e)
        logger.error(val)
    return smsg, emsg


def update_credit_to_sql():
    try:
        # transaction starts
        with transaction.atomic():
            # GASのAPI
            url = settings.URL_KAKEIBO
            r = requests.get(url+"?method=credit")
            data = r.json()
            # 登録
            for k, v in data.items():
                # Credit Item
                credititems = CreditItems.objects.filter(name=v['name'])
                if credititems.__len__() is 0:
                    new_item = CreditItems()
                    new_item.name = v['name']
                    new_item.date = v['date'][0:10]
                    new_item.save()
                    citem = new_item
                else:
                    citem = CreditItems.objects.get(name=v['name'])
                # 既存データ確認
                fee_date = parser.parse(v['date']).astimezone(timezone('Asia/Tokyo'))
                fee = v['fee']
                debit_year = "20" + v['debit_date'][0:2]
                debit_month = v['debit_date'][3:5]
                debit_date = debit_year + "-" + debit_month + "-01"
                check = Credits.objects.filter(date=fee_date, fee=fee, debit_date=debit_date).__len__()
                if check > 0:
                    continue
                # 存在しない場合のみ新規作成
                else:
                    credit = Credits()
                    credit.date = fee_date
                    credit.credit_item = citem
                    credit.fee = fee
                    credit.debit_date = debit_date
                    credit.save()
            smsg = "Updating credit-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating credit-records failed: " + str(e)
    # Dashboardへリダイレクト
    return smsg, emsg


def update_kakeibo_to_sql():
    try:
        # dateチェック
        if Kakeibos.objects.all():
            check_date = Kakeibos.objects.all().order_by('-date')[0].date
        else:
            check_date = date(2011, 1, 1)
        # transaction starts
        with transaction.atomic():
            # SSから取得
            url = settings.URL_KAKEIBO
            r = requests.get(url+"?method=kakeibo")
            data = r.json()
            for k, val in data.items():
                date_stump = parser.parse(val['タイムスタンプ']).astimezone(timezone('Asia/Tokyo')).date()
                if date_stump < check_date:
                    continue
                elif val['金額'] is not 0:
                    fee = (val['金額'])
                    way = val['項目']
                    memo = val['メモ']
                    tag = val['タグ']
                    move_to = None
                    move_from = None
                    usage = None
                    if way == "引き落とし":
                        move_from = Resources.objects.get(name=val['引き落とし対象'])
                        usage = Usages.objects.get(name=val['引き落とし項目'])
                    elif way == "振替":
                        move_from = Resources.objects.get(name=val['From'])
                        move_to = Resources.objects.get(name=val['To'])
                    elif way == "収入":
                        move_to = Resources.objects.get(name=val['振込先'])
                        if val['収入源'] == 'その他':
                            val['収入源'] = 'その他収入'
                        usage = Usages.objects.get(name=val['収入源'])
                    elif way == "支出（現金）":
                        move_from = Resources.objects.get(name='財布')
                        usage = Usages.objects.get(name=val['支出項目'])
                    elif way == "支出（クレジット）":
                        usage = Usages.objects.get(name=val['支出項目'])
                    elif way == "共通支出":
                        usage = Usages.objects.get(name="共通支出")
                        move_from = Resources.objects.get(name="財布")
                # 既存データがなければセーブ
                check = Kakeibos.objects.filter(
                    date=date_stump, fee=fee, way=way,
                    move_to=move_to, move_from=move_from, usage=usage
                ).__len__()
                if check == 0:
                    data = {
                        "date": date_stump, "fee": fee, "way": way,
                        "move_to": move_to, "move_from": move_from,
                        "usage": usage, "memo": memo, "tag": tag
                    }
                    Kakeibos(**data).save()

            smsg = "Updating kakeibo-records completed successfully"
            emsg = ""
    except Exception as e:
        smsg = ""
        emsg = "Updating kakeibo-records failed: " + str(e)
    return smsg, emsg