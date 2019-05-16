from django.shortcuts import HttpResponse, Http404, redirect
import logging
logger = logging.getLogger("django")
from asset.functions import get_info, mylib_asset, analysis_asset


def ajax_get_stock_name(request):
    if request.method == 'POST':
        name = get_info.stock_overview(request.POST['code'])['name']
        return HttpResponse(name)
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも
