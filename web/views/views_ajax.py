from django.views.generic import View
from django.http import JsonResponse
from django.contrib import messages
from web.forms import SBIAlertForm, Entry
from web.functions import data_migration, mylib_selenium, mylib_scraping
from web.models import Order, Stock
from fmanage import tasks
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging
logger = logging.getLogger('django')


class GetOrder(View):
    def get(self, request, *args, **kwargs):
        try:
            num_before = Order.objects.count()
            data_migration.stock()
            result = data_migration.order()
            num_after = Order.objects.count()
            result = {
                "status": result,
                "num_added": num_after - num_before,
            }
        except Exception as e:
            logger.warning(e)
            result = {
                "status": False,
                "num_added": 0,
            }
        finally:
            return JsonResponse(result, safe=False)


class SetAlert(View):
    def post(self, request, *args, **kwargs):
        sbialert_form = SBIAlertForm(request.POST)
        result = {
            "status": False,
            "sbialert": None,
            "msg": None
        }
        try:
            if sbialert_form.is_valid():
                sbialert = sbialert_form.save()
                task = tasks.set_alert.delay(sbialert.stock.code, sbialert.val, sbialert.type)
                result["status"] = True
                result["sbialert"] = sbialert.id
                result["task"] = task.id
                result["msg"] = "SUCEESS"
        except Exception as e:
            result["msg"] = str(e)
            logger.error(e)
        finally:
            return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class BuyOrder(View):
    def post(self, request, *args, **kwargs):
        result = {
            "status": False,
            "msg": None
        }
        try:
            logger.info("BuyOrder")
            logger.info(request.POST)
            entry_id = request.POST.get("entry", None)
            entry = Entry.objects.get(pk=entry_id)
            if entry.is_in_order or not entry.is_plan or not entry.num_plan:
                raise Exception('In Order / Not plan / NumPlan is null')
            task = tasks.set_buy_nams.delay(entry.stock.code, entry.num_plan)
            entry.is_in_order = True
            entry.save()
            result["status"] = True
            result["task"] = task.id
            result["msg"] = "SUCEESS"
        except Exception as e:
            result["msg"] = str(e)
            logger.error(e)
        finally:
            return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class ActivateEntry(View):
    def post(self, request, *args, **kwargs):
        result = {
            "status": False,
            "msg": None
        }
        try:
            logger.info("===Activate Entry===")
            logger.info(request.POST)
            entry_id = request.POST.get("entry", None)
            entry = Entry.objects.get(pk=entry_id)
            if not entry.is_plan:
                raise Exception('The entry is not plan')
            entry.is_closed = False
            entry.save()
            result["status"] = True
            result["msg"] = "SUCEESS"
            messages.success(request, "Entry {} は有効化されました".format(entry))
        except Exception as e:
            result["msg"] = str(e)
            logger.error(e)
        finally:
            return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class DeactivateEntry(View):
    def post(self, request, *args, **kwargs):
        result = {
            "status": False,
            "msg": None
        }
        try:
            logger.info("===Deactivate Entry===")
            logger.info(request.POST)
            entry_id = request.POST.get("entry", None)
            entry = Entry.objects.get(pk=entry_id)
            if not entry.is_plan:
                raise Exception('The entry is not plan')
            entry.is_closed = True
            entry.save()
            result["status"] = True
            result["msg"] = "SUCEESS"
            messages.success(request, "Entry {} は無効化されました".format(entry))
        except Exception as e:
            result["msg"] = str(e)
            logger.error(e)
        finally:
            return JsonResponse(result, safe=False)


class GetStockInfo(View):
    def get(self, request, *args, **kwargs):
        try:
            result = {
                "msg": "",
                "status": True,
                "data": {},
                "is_registered": True,
            }
            code = request.GET['code']
            d = mylib_scraping.yf_detail(code)
            if d['status']:
                result['msg'] = 'Scraping for code: {} was completed successfully'.format(code)
                result['data'] = d['data']
                result['is_registered'] = Stock.objects.filter(code=code).exists()
            else:
                raise Exception('Scraping for code: {} was failed'.format(code))
        except Exception as e:
            logger.error(e)
            result["msg"] = e.args
            result["status"] = False
        finally:
            return JsonResponse(result, safe=False)