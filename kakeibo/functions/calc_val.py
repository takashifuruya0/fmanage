# coding:utf-8

from django.conf import settings
# model
from kakeibo.models import Kakeibos, Resources
# module
import logging
logger = logging.getLogger("django")


def calc_current_val(rsname, val):
    try:
        rs = Resources.objects.get(name=rsname)
        # 初回
        if rs.current_val is None:
            move_to = Kakeibos.objects.filter(move_to=rs)
            move_from = Kakeibos.objects.filter(move_from=rs)
            rs.current_val = rs.init_val + move_to - move_from
        # 初回以外
        else:
            rs.current_val = rs.current_val + val
        rs.save()
        msg = rsname + " is updated successfully"
    except Exception as e:
        msg = "Failed to update " + rsname
    return msg
