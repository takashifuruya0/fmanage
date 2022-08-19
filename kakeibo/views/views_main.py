# coding:utf-8
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.generic import View
from django.conf import settings
from django.contrib import messages
from django.db import transaction
# csv
import csv
from io import TextIOWrapper
# logging
import logging
logger = logging.getLogger("django")
# model
from kakeibo.models import *
from kakeibo.forms import *
from datetime import date, datetime
# function
from kakeibo.functions import mylib
from kakeibo.functions.mylib import time_measure
from kakeibo.functions import process_kakeibo

# Create your views here.


@login_required
# @staff_member_required
@time_measure
def dashboard(request):
    today = date.today()
    # Form
    kakeibo_form = KakeiboForm(initial={'date': today})
    shared_form = SharedKakeiboForm(initial={'date': today})
    event_form = EventForm(initial={'date': today})
    usual_records = UsualRecord.objects.all()
    # kakeibo
    kakeibos = Kakeibos.objects.filter(date__month=today.month, date__year=today.year) \
        .select_related('usage', 'move_from', 'move_to', 'event')
    kakeibos_out = kakeibos.filter(way__in=("支出（現金）", "引き落とし"))
    kakeibos_expense = kakeibos.filter(way__in=("支出（クレジット）", "支出（現金）", "引き落とし"))
    # resource
    current_resource = Resources.objects.all() \
        .prefetch_related('move_from', 'move_to')
    # usage
    current_usage = kakeibos_expense.values('usage__name').annotate(sum=Sum('fee')).order_by("-sum")
    # event
    events = Event.objects.filter(date__year=today.year).order_by("-is_active", "-date") \
        .prefetch_related('event_kakeibo')
    event_sum_plan = events.aggregate(sum=Sum('sum_plan'))['sum']
    event_sum_actual = 0
    for event in events:
        event_sum_actual += event.sum_actual()
    # 収入・支出・総資産
    income = math.floor(mylib.cal_sum_or_0(kakeibos.filter(way="収入")))
    expense =  math.floor(mylib.cal_sum_or_0(kakeibos_out))
    total = (Kakeibos.objects.filter(move_from=None).exclude(move_to=None).aggregate(s=Sum('fee_converted'))['s'] or 0)\
        - (Kakeibos.objects.filter(move_to=None).exclude(move_from=None).aggregate(s=Sum('fee_converted'))['s'] or 0) \
        - (Kakeibos.objects.filter(move_to__name='投資口座').aggregate(s=Sum('fee'))['s'] or 0) \
        + (AssetStatus.objects.latest('date').get_total() or 0)
    # status, progress_bar
    pb_kakeibo, status_kakeibo = process_kakeibo.kakeibo_status(income, expense)
    # shared
    seisan = mylib.seisan(today.year, today.month)
    # 赤字→精算あり
    if seisan['status'] == "赤字":
        status_shared = "danger"
        pb_shared = {"in": int(seisan['budget']['sum'] / seisan['payment']['sum'] * 100), "out": 100}
    else:
        status_shared = "primary"
        pb_shared = {"in": 100, "out": int(seisan['payment']['sum'] / seisan['budget']['sum'] * 100)}
    # shared_grouped_by_usage
    shared_grouped_by_usage = SharedKakeibos.objects\
        .filter(date__month=today.month, date__year=today.year)\
        .values('usage__name').annotate(sum=Sum('fee')).order_by("-sum")
    # chart.js
    data = {
        "現金精算": [0, seisan['seisan'], 0, 0],
        "予算": [seisan['budget']['hoko'], 0, seisan['budget']['taka'], 0],
        "支払": [0, seisan['payment']['hoko'], 0, seisan['payment']['taka']],
        seisan['status']: seisan['rb'],
    }
    labels = ["朋子予算", "朋子支払", "敬士予算", "敬士支払"]
    bar_eom = {"data": data, "labels": labels}

    output = {
        "today": today,
        # kakeibo
        "inout": income-expense,
        "income": income,
        "expense": expense,
        "total": total,
        "current_usage": current_usage,
        "current_resource": current_resource,
        # shared
        "seisan": seisan,
        "shared_grouped_by_usage": shared_grouped_by_usage,
        "bar_eom": bar_eom,
        # progress bar and status
        "pb": {"kakeibo": pb_kakeibo, "shared": pb_shared},
        "status": {"kakeibo": status_kakeibo, "shared": status_shared},
        # kakeibo_form
        "kakeibo_form": kakeibo_form,
        "shared_form": shared_form,
        "username": request.user.username,
        "usual_records": usual_records,
        # events
        "events": events,
        "event_sum_actual": event_sum_actual,
        "event_sum_plan": event_sum_plan,
        "event_form": event_form,
    }
    logger.info("output: " + str(output))
    return TemplateResponse(request, 'kakeibo/dashboard.html', output)


@login_required
# @staff_member_required
@time_measure
def mine(request):
    today = date.today()
    # Form
    kakeibo_form = KakeiboForm(initial={'date': today})
    # 貯金扱いの口座
    saving_account = [r.name for r in Resources.objects.filter(is_saving=True)]
    # check year and month from GET parameter
    year, month = process_kakeibo.yearmonth(request)
    kakeibos = Kakeibos.objects.filter(date__month=month, date__year=year)
    kakeibos_out = kakeibos.filter(way__in=("支出（現金）", "引き落とし"))
    kakeibos_expense = kakeibos.filter(way__in=("支出（クレジット）", "支出（現金）", "引き落とし"))
    income = math.floor(mylib.cal_sum_or_0(kakeibos.filter(way="収入")))
    expense =  math.floor(mylib.cal_sum_or_0(kakeibos_out))
    # status, progress_bar
    pb_kakeibo, status_kakeibo = process_kakeibo.kakeibo_status(income, expense)
    # way
    current_way = kakeibos_expense.values('way').annotate(sum=Sum('fee')).order_by("-sum")
    # resource
    current_resource = Resources.objects.all()
    # usage
    current_usage = kakeibos_expense.values('usage__name').annotate(sum=Sum('fee')).order_by("-sum")
    # saved
    rs_saved = current_resource.filter(name__in=saving_account)
    move_to = mylib.cal_sum_or_0(kakeibos.filter(move_to__in=rs_saved))
    move_from = mylib.cal_sum_or_0(kakeibos.filter(move_from__in=rs_saved))
    saved = move_to - move_from
    # usage
    usages_chart = kakeibos_out.values('usage__name').annotate(sum=Sum('fee')).order_by("sum").reverse()
    # resources_year
    resources_year_chart, months_chart = process_kakeibo.resources_year_rev(12)
    # kakeibo-usage
    usage_list = [u.name for u in Usages.objects.filter(is_expense=True)]
    kakeibo_usage = process_kakeibo.usage_kakeibo_table(usage_list)
    # Consolidated_usages: dict --> [(name, val),(name, val),(name, val),...]
    consolidated_usages_chart = sorted(process_kakeibo.consolidated_usages().items(), key=lambda x: -x[1])
    cash_usages_chart = sorted(process_kakeibo.cash_usages().items(), key=lambda x: -x[1])
    # total
    total = (Kakeibos.objects.filter(move_from=None).exclude(move_to=None).aggregate(s=Sum('fee_converted'))['s'] or 0)\
        - (Kakeibos.objects.filter(move_to=None).exclude(move_from=None).aggregate(s=Sum('fee_converted'))['s'] or 0) \
        - (Kakeibos.objects.filter(move_to__name='投資口座').aggregate(s=Sum('fee'))['s'] or 0) \
        + (AssetStatus.objects.latest('date').get_total() or 0)
    total_saved = sum(rs.current_val() for rs in rs_saved)
    # 1年間での推移
    saved_one_year_ago = 0
    for ryc in resources_year_chart:
        if ryc['name'] in saving_account:
            saved_one_year_ago = ryc["val"][0]
            break
    change = {
        "total":  total - sum([i['val'][0] for i in resources_year_chart]),
        "total_saved": total_saved - saved_one_year_ago
    }
    # 年間の収入・支出
    inouts_grouped_by_months = process_kakeibo.inouts_grouped_by_months()
    # output
    output = {
        "today": {"year": year, "month": month},
        # status
        "status": status_kakeibo,
        "saved": saved,
        "inout": income - expense,
        # progress_bar
        "pb_kakeibo": pb_kakeibo,
        "income": income,
        "expense": expense,
        # current list
        "current_way": current_way,
        "current_resource": current_resource,
        "current_usage": current_usage,
        # chart js
        "usages_chart": usages_chart,
        "resources_year_chart": resources_year_chart,
        "months_chart": months_chart,
        "consolidated_usages_chart": consolidated_usages_chart,
        # kus
        "kakeibo_usage_table": kakeibo_usage,
        "usage_list": usage_list,
        # total
        "total": total,
        "total_saved": total_saved,
        "change": change,
        # igbn
        "inouts_grouped_by_months": inouts_grouped_by_months,
        # cash_usages_chart
        "cash_usages_chart": cash_usages_chart,
        # form
        "kakeibo_form": kakeibo_form,
    }
    return TemplateResponse(request, 'kakeibo/mine.html', output)


@time_measure
def shared(request):
    # POSTの場合
    if request.method == "POST":
        # new_record
        if request.POST['post_type'] == "new_record_shared":
            try:
                form = SharedKakeiboForm(request.POST)
                form.is_valid()
                form.save()
                # msg
                smsg = "New record was registered"
                messages.success(request, smsg)
                logger.info(smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)
                messages.error(request, emsg)
            finally:
                return redirect('kakeibo:shared')

    # check year and month from GET parameter
    year, month = process_kakeibo.yearmonth(request)
    year = int(year)
    month = int(month)
    # shared
    seisan = mylib.seisan(year, month)
    budget_shared = {
        "t": seisan['budget']['taka'],
        "h": seisan['budget']['hoko'],
        "all": seisan['budget']['hoko'] + seisan['budget']['taka']
    }
    expense_shared = {
        "t": seisan['payment']['taka'],
        "h": seisan['payment']['hoko'],
        "all": seisan['payment']['hoko'] + seisan['payment']['taka']
    }
    shared = SharedKakeibos.objects.filter(date__month=month, date__year=year)
    inout_shared = seisan["inout"]
    rb_name = seisan['status']
    move = seisan['seisan']
    # 赤字→精算あり
    if rb_name == "赤字":
        status_shared = "danger"
        pb_shared = {"in": int(budget_shared['all'] / expense_shared['all'] * 100), "out": 100}
    else:
        status_shared = "primary"
        pb_shared = {"in": 100, "out": int(expense_shared['all'] / budget_shared['all'] * 100)}
    # shared_grouped_by_usage
    shared_usages = shared.values('usage__name').annotate(Sum('fee'))
    # chart.js
    data = {
        "現金精算": [0, seisan['seisan'], 0, 0],
        "予算": [seisan['budget']['hoko'], 0, seisan['budget']['taka'], 0],
        "支払": [0, seisan['payment']['hoko'], 0, seisan['payment']['taka']],
        rb_name: seisan['rb'],
    }
    labels = ["朋子予算", "朋子支払", "敬士予算", "敬士支払"]
    bar_eom = {"data": data, "labels": labels}
    # 年間
    usage_list = ["家賃", "食費", "日常消耗品", "ガス", "電気", "水道", "交際費", "その他"]
    data_year = process_kakeibo.usage_shared_table(usage_list)
    # who paid ?
    who_paid = shared.values('usage__name', 'paid_by').annotate(Sum('fee'))
    # shared_form
    shared_form = SharedKakeiboForm(initial={'date': date.today()})
    # output
    output = {
        "today": {"year": year, "month": month},
        # status
        "status": status_shared,
        # progress_bar
        "pb_shared": pb_shared,
        # shared
        "inout": inout_shared,
        "budget": budget_shared,
        "expense": expense_shared,
        "move": move,
        "shared_usages": shared_usages,
        "bar_eom": bar_eom,
        # table
        "data_year": data_year,
        "usage_list": usage_list,
        # who_paid
        "who_paid": who_paid,
        # form
        "shared_form": shared_form,
    }
    return TemplateResponse(request, 'kakeibo/shared.html', output)


@login_required
# @staff_member_required
@time_measure
def credit(request):
    # check year and month from GET parameter
    year, month = process_kakeibo.yearmonth(request)
    # 今月のクレジット利用履歴と合計値
    credits_month = Credits.objects.filter(debit_date__year=year, debit_date__month=month).order_by('-fee')
    credits_sum = sum([ci.sum_credit() for ci in CreditItems.objects.all()])

    # CreditItemとusage別合計
    res_credits = dict()
    sum_usage = dict()
    for citem in CreditItems.objects.all():
        temp = {
            'name': citem.name,
            'sum': citem.sum_credit(),
            'avg': citem.avg_credit(),
            'count': citem.count_credit(),
        }
        # usageが登録されていない場合を考慮
        if citem.usage:
            temp['usage'] = citem.usage.name
            tag = citem.usage.name
        else:
            temp['usage'] = ""
            tag = "その他"

        if tag in sum_usage.keys():
            sum_usage[tag] += temp['sum']
        else:
            sum_usage[tag] = temp['sum']
        res_credits[citem.pk] = temp

    # credit_month_sum
    credits_month_sum = sum([cm.fee for cm in credits_month])

    # 支出項目の円表示
    res_sum_usage = dict()
    for k, v in sorted(sum_usage.items(), key=lambda x: -x[1]):
        res_sum_usage[k] = {"sum": v, "name": k}

    # Sumの降順に並び替え
    res_credits = sorted(res_credits.items(), key=lambda x: -x[1]['sum'])
    res_sum_usage = sorted(res_sum_usage.items(), key=lambda x: -x[1]['sum'])

    # count
    credits_month_count = credits_month.__len__()

    # return
    output = {
        "today": {"year": year, "month": month},
        "credits": res_credits,
        "sum_usage": res_sum_usage,
        "credits_sum": credits_sum,
        "credits_month": credits_month,
        "credits_month_sum": credits_month_sum,
        "credits_month_count": credits_month_count,
    }

    return TemplateResponse(request, 'kakeibo/cdashboard.html', output)


@time_measure
# @staff_member_required
def link_kakeibo_and_credit(request):
    if request.method == "POST":
        messages.info(request, request.POST)
        if request.POST['type'] == "紐付":
            if "kakeibo[]" in request.POST and "credit[]" in request.POST:
                kakeibo = Kakeibos.objects.get(id=int(request.POST['kakeibo[]']))
                if kakeibo.credits_set.count() != 0:
                    # すでに紐付いている場合、紐付け解除
                    credits_linked = kakeibo.credits_set.all()
                    for cl in credits_linked:
                        cl.kakeibo = None
                        cl.save()
                # 新たに紐付け
                credit = Credits.objects.get(id=int(request.POST['credit[]']))
                credit.kakeibo = kakeibo
                credit.save()
                # msg
                msg = "Successfully made a link between Kakeibo:" \
                      + request.POST.get('kakeibo[]', "") + " and Credit:" + request.POST.get('credit[]', "")
                messages.add_message(request, messages.SUCCESS, msg)
            else:
                # エラー
                msg = "You need to select one kakeibo and one credit"
                messages.warning(request, msg)
        elif request.POST['type'] == "作成":
            credits = Credits.objects.filter(id__in=request.POST.getlist('credit[]'))
            for credit in credits:
                kakeibo = Kakeibos()
                kakeibo.fee = credit.fee
                kakeibo.way = "支出（クレジット）"
                kakeibo.date = credit.date
                kakeibo.usage = credit.credit_item.usage
                kakeibo.memo = credit.memo
                kakeibo.save()
                credit.kakeibo = kakeibo
                credit.save()
            msg = "Successfully create Kakeibos for " \
                  + str(request.POST.getlist('credit[]')) + " and links for these"
            messages.add_message(request, messages.SUCCESS, msg)
        elif request.POST['type'] == "紐付解除":
            kakeibos = Kakeibos.objects.filter(id__in=request.POST.getlist('kakeibo[]'))
            for kakeibo in kakeibos:
                if kakeibo.credits_set.count() != 0:
                    credits_linked = kakeibo.credits_set.all()
                    for cl in credits_linked:
                        cl.kakeibo = None
                        cl.save()
            msg = "Successfully delete a link of Kakeibo:" + str(request.POST.getlist('kakeibo[]'))
            messages.add_message(request, messages.SUCCESS, msg)
        elif request.POST['type'] == "削除":
            if "kakeibo[]" in request.POST:
                k = Kakeibos.objects.filter(id__in=request.POST.getlist('kakeibo[]'))
                # messages.warning(request, k.count())
                k.delete()
                msg = "Successfully delete Kakeibo:" + str(request.POST.getlist('kakeibo[]'))
                messages.add_message(request, messages.SUCCESS, msg)
            if "credit[]" in request.POST:
                c = Credits.objects.filter(id__in=request.POST.getlist('credit[]'))
                # messages.warning(request, c.count())
                c.delete()
                msg = "Successfully delete Credit:" + str(request.POST.getlist('credit[]'))
                messages.add_message(request, messages.SUCCESS, msg)
        return redirect('kakeibo:link_kakeibo_and_credit')
    elif request.method == "GET":
        last_date = Credits.objects.latest('date').date
        condition_k = {
            "way": "支出（クレジット）",
            "date__lt": last_date,
        }
        condition_c = {
            "kakeibo": None,
        }
        if 'fee' in request.GET:
            fee = int(request.GET.get('fee'))
            condition_k['fee'] = fee
            condition_c['fee'] = fee
        if "year" in request.GET:
            year = int(request.GET.get('year'))
            condition_k['date__year'] = year
            condition_c['date__year'] = year
        if "month" in request.GET:
            month = int(request.GET.get('month'))
            condition_k['date__month'] = month
            condition_c['date__month'] = month
        # query
        kakeibo_credit = Kakeibos.objects.filter(**condition_k).order_by('date')
        credit = Credits.objects.filter(**condition_c).order_by('date')
        # kakeibo_creditのカウント
        num = 0
        for kc in kakeibo_credit:
            if kc.credits_set.count() != 1:
                num += 1
        output = {
            "last_date": last_date,
            "num": num,
            "kcs": kakeibo_credit,
            "credit": credit,
        }
        return TemplateResponse(request, 'kakeibo/link_kakeibo_and_credit.html', output)


# @method_decorator(staff_member_required, name='dispatch')
class ReadCSVView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                today = date.today()
                debit_date = datetime.strptime(request.POST['debit_date'], "%Y-%m-%d").date()
                logger.info("Debit Date: {}/{}".format(debit_date.year, debit_date.month))
                form_data = TextIOWrapper(request.FILES['csv'].file, encoding='shift-jis')
                csv_file = csv.reader(form_data)
                logger.info(next(csv_file))
                for line in csv_file:
                    # CreditItemの指定or作成
                    cis = CreditItems.objects.filter(name=line[1])
                    if cis.exists():
                        ci = cis[0]
                    else:
                        ci = CreditItems.objects.create(name=line[1], date=today)
                    # 最下行以外を登録
                    d = line[0].split("/")
                    if len(d) == 3:
                        Credits.objects.create(
                            credit_item=ci,
                            date=date(int(d[0]), int(d[1]), int(d[2])),
                            fee=line[5],
                            debit_date=date(debit_date.year, debit_date.month, 1),
                            memo=line[6]
                        )
                    else:
                        Kakeibos.objects.create(
                            date=date(debit_date.year, debit_date.month, 1),
                            fee=line[5],
                            way="引き落とし",
                            usage=Usages.objects.get(name="クレジット（個人）"),
                            move_from=Resources.objects.get(name="ゆうちょ"),
                            memo="SFC {}/{}".format(debit_date.year, debit_date.month),
                        )
                        smsg = "Total {} / ".format(line[5])
                process_kakeibo.link_credit_kakeibo()
                smsg = smsg + "Credit records were created"
                messages.success(request, smsg)
                logger.info(smsg)
        except Exception as e:
            emsg = e
            logger.error(emsg)
            messages.error(request, emsg)
        finally:
            return redirect('kakeibo:dashboard')


@method_decorator(staff_member_required, name='dispatch')
class UsualRecordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            today = date.today()
            ur = UsualRecord.objects.get(id=request.POST['usual_id'])
            data = {
                "fee": ur.fee,
                "way": ur.way,
                "usage": ur.usage,
                "move_to": ur.move_to,
                "move_from": ur.move_from,
                "memo": ur.memo,
                "date": today,
                "currency": ur.currency,
            }
            Kakeibos.objects.create(**data)
            messages.success(request, "{} {} was created".format(ur.memo, ur.fee_yen()))
        except Exception as e:
            logger.error(e)
            messages.error(request, "UsualRecord: {}".format(e))
        finally:
            return redirect('kakeibo:dashboard')


@time_measure
def test(request):
    if request.method == "POST":
        if "kakeibo" in request.POST and "credit" in request.POST:
            kakeibo = Kakeibos.objects.get(id=int(request.POST['kakeibo']))
            credit = Credits.objects.get(id=int(request.POST['credit']))
            credit.kakeibo = kakeibo
            credit.save()
            msg = "Successfully made a link between Kakeibo:" + request.POST['kakeibo'] + " and " + "Credit:" + request.POST['credit']
            messages.success(request, msg)
        else:
            msg = "You need to select one kakeibo and one credit"
            messages.warning(request, msg)
        return redirect('kakeibo:test')
    else:
        kakeibo_credit = Kakeibos.objects.filter(way="支出（クレジット）").order_by('date')
        num = 0
        for kc in kakeibo_credit:
            if kc.credits_set.count() != 1:
                num += 1
        credit = Credits.objects.filter(kakeibo=None).order_by('date')
        output = {
            "num": num,
            "kcs": kakeibo_credit,
            "credit": credit,
        }
        return TemplateResponse(request, 'kakeibo/test.html', output)

