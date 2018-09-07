# coding: utf-8
from django.db.models import Sum, Avg
from django.conf import settings
from kakeibo.models import SharedKakeibos
from datetime import date
import time
# logging
import logging
logger = logging.getLogger("django")


# calculate sum or 0
def cal_sum_or_0(model):
    if model.__len__() == 0:
        return 0
    else:
        return model.aggregate(Sum('fee'))['fee__sum']


# calculate avg or 0
def cal_avg_or_0(model):
    if model.__len__() == 0:
        return 0
    else:
        return model.aggregate(Avg('fee'))['fee__avg']


def seisan(year=date.today().year, month=date.today().month):
    budget = dict()
    payment = dict()
    sk = SharedKakeibos.objects.filter(date__year=year, date__month=month)
    budget['taka'] = settings.BUDGET_TAKA
    budget['hoko'] = settings.BUDGET_HOKO
    budget['sum'] = sum(budget.values())
    payment['taka'] = cal_sum_or_0(sk.filter(paid_by="敬士"))
    payment['hoko'] = cal_sum_or_0(sk.filter(paid_by="朋子"))
    payment['sum'] = sum(payment.values())
    inout = budget['sum'] - payment['sum'] 
    # 赤字→精算あり
    if inout <= 0:
        inout = -inout
        rb = [int(inout/2), 0, int(inout/2), 0]
        rb_name="赤字"
        seisan = int(inout / 2) + budget['hoko'] - payment['hoko']
    # 黒字＋朋子さん支払いが朋子さん予算以下→精算あり
    elif -inout + budget['hoko'] - payment['hoko'] >= 0:
        rb = [0, inout, 0, 0]
        rb_name = "黒字"
        seisan = -inout + budget['hoko'] - payment['hoko']
    # 黒字＋朋子さん支払い＜朋子さん予算→精算なし
    else:
        rb = [
            0, budget['hoko'] - payment['hoko'], 
            0, inout - budget['hoko'] + payment['hoko']
        ]        
        rb_name = "黒字"
        seisan = 0
    data = {
        "date": {
            "year": year,
            "month": month,
        },
        "seisan": seisan,
        "budget": budget,
        "payment": payment,
        "inout": inout,
        "status": rb_name,
        "rb": rb,
    }

    return data


def time_start():
    return time.time()


def time_end(start):
    return time.time()-start


def time_measure(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        res = func.__name__ + " " + str(end-start)
        logger.info(res)
        return result
    return wrapper

