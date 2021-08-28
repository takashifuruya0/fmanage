from kakeibo.models import Kakeibos, Usages, SharedKakeibos, Resources, Credits, CreditItems, Budget
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Avg, Q, Count
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
# function
from kakeibo.functions.mylib import time_measure
# asset
# from asset.models import AssetStatus
from web.models import AssetStatus
# logging
import logging
logger = logging.getLogger("django")


@time_measure
def usage_shared_table(usage_list):
    today = date.today()
    # e.g. 2019/11/30
    this_month = date(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    # e.g. 2018/12/31 ~ 2019/11/30
    target_range = [this_month + relativedelta(months=-12, days=1), this_month]
    suy = SharedKakeibos.objects.filter(date__range=target_range) \
        .annotate(month=TruncMonth('date')) \
        .values('month', 'usage').order_by('month') \
        .annotate(sum=Sum('fee'))
    # data用意
    data_year = [
        {
            "budget_shared": Budget.objects.filter(date__lte=(this_month-relativedelta(months=i))).latest('date').total(),
            "year": (this_month-relativedelta(months=i)).year,
            "month": (this_month-relativedelta(months=i)).month,
            "sum": "",
            "color": "",
            "percent": "",
            "data": [0 for j in range(len(usage_list))]
        } for i in range(12)
    ]
    month_order = {
        (this_month - relativedelta(months=i)).month: i for i in range(12)
    }
    usage_names = {u.pk: u.name for u in Usages.objects.all()}
    for s in suy:
        name = usage_names[s['usage']]
        for u in range(len(usage_list)):
            if name == usage_list[u]:
                data_year[month_order[s['month'].month]]['data'][u] = s['sum']
    for i in range(12):
        data_year[i]['sum'] = sum(data_year[i]['data'])
        data_year[i]["percent"] = data_year[i]['sum'] / (data_year[i]['budget_shared'] + 30000) * 100
        data_year[i]["color"] = "success" if data_year[i]['sum'] < data_year[i]['budget_shared'] else "danger"
    return data_year


@time_measure
def usage_kakeibo_table(usage_list):
    today = date.today()
    # e.g. 2019/11/30
    this_month = date(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    # e.g. 2018/12/31 ~ 2019/11/30
    target_range = [this_month + relativedelta(months=-12, days=1), this_month]
    # kakeibos
    kakeibos = Kakeibos.objects.exclude(usage=None).filter(date__range=target_range) \
        .annotate(month=TruncMonth('date')) \
        .values('month', 'usage').order_by('month') \
        .annotate(sum=Sum('fee'))
    # data用意
    data_year = [
        {
            "year": (this_month - relativedelta(months=i)).year,
            "month": (this_month-relativedelta(months=i)).month,
            "sum": "",
            "data": [0 for j in range(len(usage_list))]
        } for i in range(12)
    ]
    month_order = {
        (this_month - relativedelta(months=i)).month: i for i in range(12)
    }
    # pk:name のdictを用意
    usage_names = {u.pk: u.name for u in Usages.objects.all()}
    for s in kakeibos:
        name = usage_names[s['usage']]
        for u in range(len(usage_list)):
            if name == usage_list[u]:
                data_year[month_order[s['month'].month]]['data'][u] = s['sum']
    for i in range(12):
        data_year[i]['sum'] = sum(data_year[i]['data'])
    return data_year


@time_measure
def yearmonth(request):
    if request.GET.get(key="yearmonth") is not None:
        year = request.GET.get(key="yearmonth")[0:4]
        month = request.GET.get(key="yearmonth")[5:]
    else:
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
    if year is None or month is None:
        year = date.today().year
        month = date.today().month
    return year, month


@time_measure
def consolidated_usages():
    # responseの型を設定
    usages = Usages.objects.filter(is_expense=True)
    res = {u.name: 0 for u in usages}
    # Kakeibos
    kus = Kakeibos.objects.exclude(usage=None).exclude(usage__is_expense=False).values('usage').annotate(sum=Sum('fee'))
    uname = {u.pk: u.name for u in Usages.objects.all()}
    for ku in kus:
        name = uname[ku['usage']]
        res[name] += ku['sum']
    # Credits
    cis = CreditItems.objects.all()
    for ci in cis:
        c_sum = Credits.objects.filter(credit_item=ci).aggregate(Sum('fee'))['fee__sum']
        try:
            res[ci.usage.name] += c_sum
        # CreditItemsとUsagesの紐づけがされていない場合→その他へ
        except Exception as e:
            if c_sum:
                res["その他"] += c_sum
    # クレジットは削除
    for i in ["クレジット（個人）", "クレジット（家族）"]:
        if i in res.keys():
            res.pop(i)
    # 0件のものは削除
    del_keys = list()
    for k, u in res.items():
        if u == 0:
            del_keys.append(k)
    for k in del_keys:
        res.pop(k)
    return res


@time_measure
def resources_year_rev(num=12):
    resources = Resources.objects.all()
    resources_year_chart = [{"name": r.name, "val": [r.current_val() for j in range(num)]} for r in resources]

    # months_chart: monthの古い順リスト
    today = date.today()
    months = [(today + relativedelta(months=-i)) for i in range(num)]
    months_chart = [(str(m.year) + "/" + str(m.month)) for m in months]
    months_chart.reverse()

    start_month = today + relativedelta(months=-num)
    kfs = Kakeibos.objects.exclude(move_from=None).exclude(date__lt=start_month)\
        .annotate(month=TruncMonth('date'))\
        .values('month', 'move_from').annotate(sum=Sum('fee'))
    kts = Kakeibos.objects.exclude(move_to=None).exclude(date__lt=start_month)\
        .annotate(month=TruncMonth('date'))\
        .values('month', 'move_to').annotate(sum=Sum('fee'))

    # resources_year_chartにおける、resources の順番
    resources_order = dict()
    cnt = 0
    resource_ids = {r.name: r.pk for r in resources}
    for r in resources_year_chart:
        resources_order[resource_ids[r['name']]] = cnt
        cnt += 1

    # xn = current_val - sum(t)^c_(n+1) + sum(f)^c_(n+1)
    for kf in kfs:
        # 今月と対象月の差分月数
        diff = (today.year - kf['month'].year) * 12 + (today.month - kf['month'].month)
        # diff = 0 ~ num-2
        if diff >= num-1:
            continue
        else:
            cnt_f = resources_order[kf['move_from']]
            for i in range(0, num-diff-1):
                resources_year_chart[cnt_f]['val'][i] += kf['sum']

    for kt in kts:
        diff = (today.year - kt['month'].year) * 12 + (today.month - kt['month'].month)
        if diff >= num:
            continue
        else:
            cnt_t = resources_order[kt['move_to']]
            for i in range(0, num-diff-1):
                resources_year_chart[cnt_t]['val'][i] -= kt['sum']

    # 投資口座
    atotal_initial = AssetStatus.objects.first().get_total()
    for i, r in enumerate(resources_year_chart):
        # 投資口座のデータを削除
        if r['name'] == "投資口座":
            resources_year_chart.pop(i)
            break
    # 追加データ
    add = {
        "name": "投資口座",
        "val": [atotal_initial for j in range(num)]
    }
    for i, mc in enumerate(months_chart):
        year = int(mc.split("/")[0])
        month = int(mc.split("/")[1])
        astatus = AssetStatus.objects.filter(date__year=year, date__month=month)
        if astatus:
            add['val'][i] = astatus.last().get_total()
        elif today.year == year and today.month == month:
            add['val'][i] = AssetStatus.objects.last().get_total()
        else:
            # データがない場合は0
            add['val'][i] = 0
    resources_year_chart.append(add)
    return resources_year_chart, months_chart


@time_measure
def kakeibo_status(income, expense):
    # status, progress_bar
    try:
        if income > expense:
            status_kakeibo = "primary"
            pb_kakeibo = {"in": 100, "out": int(expense / income * 100)}
        else:
            status_kakeibo = "danger"
            pb_kakeibo = {"in": int(income / expense * 100), "out": 100}
    except Exception as e:
        logger.error("Failed to set status and progress_bar")
        status_kakeibo = "primary"
        pb_kakeibo = {"in": 100, "out": 100}
    return pb_kakeibo, status_kakeibo


def inouts_grouped_by_months():
    res = {
        "month": list(),
        "expense": list(),
        "income": list(),
    }
    # inouts_grouped_by_months
    igbn = Kakeibos.objects.exclude(usage=None).annotate(month=TruncMonth('date'))\
        .values('month', 'usage__is_expense').annotate(sum=Sum('fee'))
    today = date.today()
    this_month = date(today.year, today.month, 1)
    for i in range(12):
        month = this_month + relativedelta(months=i-11)
        res['month'].append(month)
        try:
            res['expense'].append(igbn.get(usage__is_expense=True, month=month)['sum'])
        except Exception as e:
            logger.error(e)
            res['expense'].append(0)
        try:
            res['income'].append(igbn.get(usage__is_expense=False, month=month)['sum'])
        except Exception as e:
            logger.error(e)
            res['income'].append(0)
    return res


def usages_grouped_by_months():
    res = {
        "month": list(),
        "usages": dict()
    }
    usages = Usages.objects.filter(is_expense=True)
    for u in usages:
        res['usages'][u.name] = list()
    # usages_grouped_by_months
    ugbn = Kakeibos.objects.exclude(usage=None).annotate(month=TruncMonth('date'))\
        .values('month', 'usage').annotate(sum=Sum('fee'))
    today = date.today()
    this_month = date(today.year, today.month, 1)
    for i in range(12):
        month = this_month + relativedelta(months=i-11)
        res['month'].append(month)
        for u in usages:
            try:
                res['usages'][u.name].append(ugbn.get(usage=u.pk, month=month)['sum'])
            except Exception as e:
                # 該当月に対象usageのレコードがない場合
                logger.debug(e)
                res['usages'][u.name].append(0)
    # 0件のものは削除
    del_keys = list()
    for k, u in res['usages'].items():
        if sum(u) == 0:
            del_keys.append(k)
    for k in del_keys:
        res['usages'].pop(k)
    return res


@time_measure
def cash_usages():
    # responseの型を設定
    usages = Usages.objects.filter(is_expense=True)
    res = {u.name: 0 for u in usages}
    # Kakeibos
    kus = Kakeibos.objects.exclude(usage=None).exclude(usage__is_expense=False).values('usage').annotate(sum=Sum('fee'))
    uname = {u.pk: u.name for u in Usages.objects.all()}
    for ku in kus:
        name = uname[ku['usage']]
        res[name] += ku['sum']
    # クレジットは削除
    for i in ["クレジット（個人）", "クレジット（家族）"]:
        if i in res.keys():
            res.pop(i)
    return res


def link_credit_kakeibo():
    credits = Credits.objects.all()
    kcs = Kakeibos.objects.filter(way="支出（クレジット）")
    other = Usages.objects.get(name="その他")
    counter = [0, 0, 0, 0]
    msgs = []
    for c in credits:
        try:
            if c.kakeibo:
                continue
            check = kcs.filter(fee=c.fee, date__year=c.date.year, date__month=c.date.month)
            num = check.count()
            if num == 1 and check[0].credits_set.count() == 0:
                c.kakeibo = check[0]
                c.save()
                counter[1] += 1
            elif num == 0:
                # 前後月で該当しないかチェック
                check2 = kcs.filter(fee=c.fee, date__year=c.date.year,
                                    date__month__in=(c.date.month + 1, c.date.month - 1))
                if check2.count() == 1:
                    c.kakeibo = check2[0]
                    c.save()
                    continue
                # 新規作成
                k = Kakeibos()
                k.date = c.date
                k.fee = c.fee
                k.way = "支出（クレジット）"
                if c.credit_item:
                    k.usage = c.credit_item.usage
                    k.memo = c.credit_item.name
                else:
                    k.usage = other
                k.save()
                c.kakeibo = k
                c.save()
                counter[0] += 1
            else:
                for ck in check:
                    if ck.usage == c.credit_item.usage and ck.credits_set.count() == 0:
                        c.kakeibo = ck
                        c.save()
                        counter[2] += 1
                        break
                    else:
                        msgs.append("{} is not {}".format(c.credit_item.usage, ck.usage))
                        pass

        except Exception as e:
            logger.error(e)
            return
    smsg = "0:{}, 1:{}, matched:{}".format(counter[0], counter[1], counter[2])
    logger.info(smsg)
    return smsg, msgs
