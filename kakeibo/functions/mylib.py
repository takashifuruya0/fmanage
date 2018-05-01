# coding: utf-8
from django.db.models import Sum, Avg


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
