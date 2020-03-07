from django.views.generic import View
from django.http import JsonResponse
from web.functions import data_migration
from web.models import Order
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
