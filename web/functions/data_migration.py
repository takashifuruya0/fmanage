from web.models import *
import requests
from datetime import datetime
from django.contrib.auth.models import User
from web.functions import mylib_asset
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
                    Order.objects.filter(pk=o.pk).update(**d)
                    o = Order.objects.get(pk=o.pk)
                else:
                    o = Order.objects.create(**d)
                    logger.info("Order process for {} is starting in data_migration.order().")
                    mylib_asset.order_process(o, user)
                    logger.info("Order process for {} completed in data_migration.order().")
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
                astatus = AssetStatus.objects.create(**dm)
                if dm['date'] == date.today():
                    astatus.update_status()
                    logger.info("Today's AssetStatus {} is updated".format(astatus))
                astatus_list.append(astatus)
        # result = AssetStatus.objects.bulk_create(astatus_list)
        # 今日の日付は更新
        # if AssetStatus.objects.filter(date=date.today()).count() == 1:
        #     AssetStatus.objects.get(date=date.today()).update_status()
    return astatus_list


def entrystatus():
    data = [
        {
            "status": "1_swing",
            "definition": "",
            "entry_type": "短期",
            "min_profit_percent": None,
            "max_holding_period": 5,
            "is_within_week": True,
            "is_within_holding_period": True,
        },
        {
            "status": "2_急騰",
            "definition": "短期間で売り抜ける",
            "entry_type": "短期",
            "min_profit_percent": 5,
            "max_holding_period": 13,
            "is_within_week": False,
            "is_within_holding_period": True,
        },
        {
            "status": "3_売り逃げ判断",
            "definition": "今後大きな利益が出るかを見極め。利益が出ている間に売り逃げる手も有り",
            "entry_type": "中期",
            "min_profit_percent": None,
            "max_holding_period": 30,
            "is_within_week": False,
            "is_within_holding_period": True,
        },
        {
            "status": "4_上昇トレンド乗り",
            "definition": "トレンドに乗ったことを確認し、利益を上げる。最低限の利益は得たいので、下げたら売ってしまうも良し",
            "entry_type": "中期",
            "min_profit_percent": 5,
            "max_holding_period": 60,
            "is_within_week": False,
            "is_within_holding_period": True,
        },
        {
            "status": "5_判断中（含み損）",
            "definition": "含み損が出ているが、上昇チャンスに期待し耐えている状態。損切りライン超えと長期化は避ける",
            "entry_type": "中期",
            "min_profit_percent": -10,
            "max_holding_period": 90,
            "is_within_week": False,
            "is_within_holding_period": True,
        },
        {
            "status": "6_判断中（含み益）",
            "definition": "一度下がったが含み益が出始めた状態。天井探りができそうな勢いを持つ以外は、長期化を避ける",
            "entry_type": "中期",
            "min_profit_percent": None,
            "max_holding_period": 90,
            "is_within_week": False,
            "is_within_holding_period": True,
        },
        {
            "status": "7_天井探り",
            "definition": "足切りラインを10 % から徐々に上げていきながら、逆指値を設定",
            "entry_type": "中期",
            "min_profit_percent": 10,
            "max_holding_period": 90,
            "is_within_week": False,
            "is_within_holding_period": False,
        },
        {
            "status": "8_積立中",
            "definition": "積立中",
            "entry_type": "長期",
            "min_profit_percent": None,
            "max_holding_period": 1000,
            "is_within_week": False,
            "is_within_holding_period": False,
        },
        {
            "status": "9_リバランス検討",
            "definition": "リバランス検討",
            "entry_type": "長期",
            "min_profit_percent": None,
            "max_holding_period": 2000,
            "is_within_week": False,
            "is_within_holding_period": False,
        },
    ]
    try:
        for d in data:
            EntryStatus.objects.create(**d)
        return True
    except Exception as e:
        logger.warning(e)
        return False