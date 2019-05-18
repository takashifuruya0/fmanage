from django.shortcuts import HttpResponse, Http404, redirect
import logging
logger = logging.getLogger("django")
from asset.functions import get_info, mylib_asset, analysis_asset
import json


def ajax_get_stock_name(request):
    if request.method == 'POST':
        res = get_info.stock_overview(request.POST['code'])
        json_str = json.dumps(res, ensure_ascii=False, indent=2)
        return HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも
