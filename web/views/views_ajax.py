from django.views.generic import View
from django.http import JsonResponse
from web.forms import SBIAlertForm
from web.functions import data_migration, selenium_sbi
from web.models import Order
from fmanage import tasks
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




