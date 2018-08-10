# coding:utf-8

from django.conf import settings
# model
from kakeibo.models import Kakeibos, Resources
from kakeibo.functions import mylib
# module
import logging
logger = logging.getLogger("django")


def resource_current_val(rsname, val):
    try:
        rs = Resources.objects.get(name=rsname)
        # 初回
        if rs.current_val is None:
            move_to = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_to=rs))
            move_from = mylib.cal_sum_or_0(Kakeibos.objects.filter(move_from=rs))
            rs.current_val = rs.initial_val + move_to - move_from
        # 初回以外
        else:
            rs.current_val = rs.current_val + val
        rs.save()
        logger.info(rsname+":"+str(rs.current_val))
        msg = rsname + " is updated successfully"
        status = True
    except Exception as e:
        msg = "Failed to update " + rsname
        logger.error(msg)
        msg = msg + ": " + str(e)
        status = False
    res = {
        "msg": msg,
        "status": status
    }
    return res
