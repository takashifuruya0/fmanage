# coding:utf-8

from django.http import HttpResponse
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
mpl.rcParams.update({'font.size': 17})
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from kakeibo.functions import update_records, money


# basic: 円グラフ作成
def fig_pie_basic(data={}, figtitle="", colors=[], threshold=5, figsize=(8, 8), figid=1):
    """
    円グラフ作成
    :param data:  dict
    :param figtitle: title
    :param colors: list
    :param threshold: int
    :param figsize: (int, int)
    :param figid: unique id
    :return: response
    """
    # make_autopct
    def make_autopct(sum_v):
        def my_autopct(pct):
            total = sum_v
            val = int((pct * total / 100.0) + 0.5)
            if pct > threshold:
                return '{p:.0f}%  [¥{v:,}]'.format(p=pct, v=val)
            else:
                return ''
        return my_autopct

    # prepare
    labels = list()
    datas = list()
    sum_v = sum(data.values())
    for k, v in data.items():
        if isinstance(v, int) or isinstance(v, float):
            datas.append(v)
            if v / sum_v > threshold / 100:
                labels.append(k)
            else:
                labels.append("")
        else:
            datas.append(0)

    # create figure
    fig = plt.figure(figid, figsize=figsize)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.075, bottom=0.05, right=0.95, top=0.95, wspace=0.05, hspace=0.05)
    ax.set_title(figtitle)
    ax.axis("equal")
    if colors.__len__() is data.__len__():
        pie, text, autotexts = ax.pie(datas, startangle=90, labels=labels, autopct=make_autopct(sum_v), colors=colors,
                                  counterclock=False,)
    else:
        pie, text, autotexts = ax.pie(datas, startangle=90, labels=labels, autopct=make_autopct(sum_v),
                                      counterclock=False, )
    # translate into Japanese
    FONT_PATH = 'document/font/ipaexg.ttf'
    prop = mpl.font_manager.FontProperties(fname=FONT_PATH)
    plt.setp(text, fontproperties=prop)

    # return response-data
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response


def fig_bars_basic(data={}, vbar_labels = [], figtitle="", figsize=(8, 8), figid=2):
    """
    複数の棒グラフ
    :param data: listにlistを内包
    :param figtitle: タイトル
    :param figsize: (int, int)
    :param figid: int
    :return: response
    """
    if not data:
        data = {
            "a": [200, 200],
            "b": [1000, 800],
            "c": [100, 100],
            "d": [300, 500],
        }

    numdata = data.__len__()
    height = list()
    keys_legend = list()
    labels = list()
    label_positions = list()
    left_positions = list()
    vbar = 0
    for k, v in data.items():
        if vbar is 0:
            numbars = v.__len__()
            sum_v = [0 for i in range(numbars)]
        vbar = np.array(v) + vbar
        height.append(np.array(v))
        keys_legend.append(k)
        tmp = 0
        for val in v:
            if val is not 0:
                labels.append(money.convert_yen(val))
                left_positions.append(tmp)
                label_positions.append(sum_v[tmp] + val/2)
                sum_v[tmp] = sum_v[tmp] + val
            else:
                labels.append("")
                left_positions.append("")
                label_positions.append("")
            tmp += 1

    left = np.array([i for i in range(numbars)])
    hbar = [0,]
    hbar_labels = ["¥0", ]
    for i in sorted(vbar):
        hbar.append(i)
        hbar_labels.append("¥"+str(i))

    # create figure
    fig = plt.figure(figid, figsize=figsize)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.125, bottom=0.085, right=0.95, top=0.95, wspace=0.05, hspace=0.05)

    # bar
    bars = list()
    for i in range(0, numdata):
        left_position1 = left_positions[2 * i]
        label_position1 = label_positions[2 * i]
        left_position2 = left_positions[2 * i + 1]
        label_position2 = label_positions[2 * i + 1]
        label = labels[i]
        if i == 0:
            bars.append(ax.bar(left, height[i]))
            bottom = np.array(height[i])
        else:
            bars.append(ax.bar(left, height[i], bottom=bottom))
            bottom = np.array(height[i] + bottom)
        ax.text(left_position1, label_position1, label, horizontalalignment='center',
                verticalalignment='center')
        ax.text(left_position2, label_position2, label, horizontalalignment='center',
                verticalalignment='center')

    ax.legend(bars, keys_legend)
    ax.set_xticks([i for i in range(numbars)])
    ax.set_xticklabels(vbar_labels, fontsize='small')
    ax.set_yticks(hbar)
    ax.set_yticklabels(hbar_labels, fontsize='small')
    ax.set_title(figtitle)
    ax.yaxis.grid()

    # return response-data
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response
