from web.models import *
import requests
from datetime import datetime
from django.contrib.auth.models import User
from web.functions import asset_lib
from django.db import transaction
import logging
logger = logging.getLogger('django')


@transaction.atomic
def stock():
    stock_list = list()
    try:
        url = "https://www.fk-management.com/drm/asset/stock/?limit=1000&offset=0"
        r = requests.get(url)
        data = r.json()
        with transaction.atomic():
            for d in data['results']:
                d['is_trust'] = False if len(d['code']) == 4 else True
                d['fkmanage_id'] = d['pk']
                d.pop('pk')
                s = Stock.objects.filter(code=d['code'])
                if s.count() == 1:
                    s.update(**d)
                else:
                    stock_list.append(Stock(**d))
            result = Stock.objects.bulk_create(stock_list)
    except Exception as e:
        logger.error(e)
        result = False
    finally:
        return result


@transaction.atomic
def order():
    try:
        user = User.objects.first()
        url = "https://www.fk-management.com/drm/asset/order/?limit=200&offset=0"
        r = requests.get(url)
        data = r.json()
        logger.info("========data========")
        logger.info(data)
        with transaction.atomic():
            for d in data['results']:
                stock = Stock.objects.get(code=d['stock']['code'])
                d['stock'] = stock
                d['val'] = d['price']
                d['is_simulated'] = False
                d['is_buy'] = True if d['order_type'] == "現物買" else False
                d['user'] = user
                d['fkmanage_id'] = d['pk']
                d.pop('pk')
                d.pop('price')
                d.pop('order_type')
                d.pop('chart')
                os = Order.objects.filter(fkmanage_id=d['fkmanage_id'])
                logger.info("========d========")
                logger.info(d)
                if os.exists():
                    o = os.first()
                    if o:
                        Order.objects.filter(pk=o.pk).update(**d)
                        o = Order.objects.get(pk=o.pk)
                    else:
                        continue
                else:
                    o = Order.objects.create(**d)
                    asset_lib.order_process(o, user)
                # entry
                if not o.stock.is_trust and o.is_buy and not o.entry:
                    ed = {
                        "user": user,
                        "stock": stock,
                        "is_simulated": False,
                        "is_nisa": d['is_nisa'],
                    }
                    entry = Entry.objects.create(**ed)
                    o.entry = entry
                    o.save()
            result = True
    except Exception as e:
        logger.error(e)
        result = False
    finally:
        return result

    # d = {
    #     "datetime": None,
    #     "order_type": "",
    #     "stock": {
    #         "code": "",
    #         "name": "",
    #         "industry": "",
    #         "market": ""
    #     },
    #     "num": None,
    #     "price": None,
    #     "commission": None,
    #     "is_nisa": False,
    #     "chart": None
    # }


def astatus():
    date_format = "%Y-%m-%d"
    url = "https://www.fk-management.com/drm/asset/status/?limit=1000"
    user = User.objects.first()
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()['results']
        data_mapped = list(map(
            lambda x:
            {
                "user": user,
                "date": datetime.strptime(x['date'], date_format).date(),
                "investment": x['investment'],
                "sum_other": 0,
                "sum_trust": x['other_value'],
                "sum_stock": x['stocks_value'],
                "buying_power": x['buying_power'],
                "nisa_power": 1000000,
            }, data))
        astatus_list = list()
        existing_astatus_date = [a.date for a in AssetStatus.objects.all()]
        for dm in data_mapped:
            if not dm['date'] in existing_astatus_date:
                astatus_list.append(AssetStatus(**dm))
        result = AssetStatus.objects.bulk_create(astatus_list)
    return result

