from django.shortcuts import render
from kakeibo.models import Kakeibos, Usages, Resources
import json
from datetime import date, datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@csrf_exempt
def kakeibo(request):
    # add data to DB
    if request.method == "POST":
        val = json.loads(request.body.decode())
        try:
            kakeibo = Kakeibos()
            kakeibo.date = date.today()
            kakeibo.fee = (val['金額'])
            kakeibo.way = val['項目']
            kakeibo.memo = val['メモ']
            kakeibo.tag = val['タグ']

            if kakeibo.way == "引き落とし":
                kakeibo.move_from = Resources.objects.get(resource=val['引き落とし対象'])
                kakeibo.usage = Usages.objects.get(usage=val['引き落とし項目'])
            elif kakeibo.way == "振替":
                kakeibo.move_from = Resources.objects.get(resource=val['From'])
                kakeibo.move_to = Resources.objects.get(resource=val['To'])
            elif kakeibo.way == "収入":
                kakeibo.move_to = Resources.objects.get(resource=val['振込先'])
                kakeibo.usage = Usages.objects.get(usage=val['収入源'])
            elif kakeibo.way == "支出（現金）":
                kakeibo.move_from = Resources.objects.get(resource='財布')
                kakeibo.usage = Usages.objects.get(usage=val['支出項目'])
            elif kakeibo.way == "支出（クレジット）":
                kakeibo.usage = Usages.objects.get(usage=val['支出項目'])
            elif kakeibo.way == "共通支出":
                kakeibo.usage = Usages.objects.get(usage="共通支出")
            # save
            kakeibo.save()
            memo = "Success"

        except Exception as e:
            memo = e

    else:
        memo = "you should use POST"

    # json
    data = {"memo": memo, }
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response
