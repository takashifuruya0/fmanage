# coding:utf-8

from django.http import HttpResponse, Http404
import itertools
from django.conf import settings
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
mpl.rcParams.update({'font.size': 17})
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from kakeibo.functions import money
# logging
import logging
logger = logging.getLogger("django")
# Japanese
prop = mpl.font_manager.FontProperties(fname=settings.FONT_PATH)


# basic: 円グラフ作成
def fig_pie_basic(data={}, figtitle="", threshold=5, figsize=(8, 8), figid=1):
    """
    円グラフ作成
    :param data:  dict
    :param figtitle: title
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
    if sum_v is 0:
        raise Http404
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
    ax.axis("equal")

    pie, text, autotexts = ax.pie(datas, startangle=90, labels=labels, autopct=make_autopct(sum_v),
                                      counterclock=False, )
    # translate into Japanese
    plt.setp(text, fontproperties=prop)
    ax.set_title(figtitle, fontproperties=prop)

    # return response-data
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response


# basic: 円グラフ作成
def fig_pie_basic_colored(data={}, figtitle="", colors={}, threshold=5, figsize=(8, 8), figid=2):
    """
    円グラフ作成
    :param data:  dict
    :param figtitle: title
    :param colors: dict
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
    colors_graph = list()
    sum_v = sum(data.values())
    if sum_v is 0:
        raise Http404
    for k, v in data.items():
        if isinstance(v, int) or isinstance(v, float):
            datas.append(v)
            colors_graph.append(colors[k])
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
    ax.axis("equal")
    if colors_graph.__len__() is data.__len__():
        pie, text, autotexts = ax.pie(datas, startangle=90, labels=labels, autopct=make_autopct(sum_v),
                                      colors=colors_graph,
                                      counterclock=False,)
    else:
        logger.info("A figure was created with default colors since size of color-list unmatched")
        pie, text, autotexts = ax.pie(datas, startangle=90, labels=labels, autopct=make_autopct(sum_v),
                                      counterclock=False, )
    # translate into Japanese
    plt.setp(text, fontproperties=prop)
    ax.set_title(figtitle, fontproperties=prop)

    # return response-data
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response


def fig_bars_basic_color(data={}, vbar_labels = [], colors={}, figtitle="", figsize=(8, 8), figid=3):
    """
    複数の棒グラフ
    :param data: listにlistを内包
    :param figtitle: タイトル
    :param figsize: (int, int)
    :param figid: int
    :param colors: dict
    :return: response
    """
    if not data:
        data = {
            "a": [200, 200],
            "b": [1000, 800],
            "c": [100, 100],
            "d": [300, 500],
        }

    height = list()  # データ
    numdata = data.__len__()  # データ個数
    keys_legend = list()  # データ名
    labels = list()  # データラベル
    label_positions = list()  # labelのy位置
    left_positions = list()  # labelのx位置
    colors_graph = list()  # graphの色
    vbar = 0
    for k, v in data.items():
        if vbar is 0:
            numbars = v.__len__()  # 棒の数
            sum_v = [0 for i in range(numbars)]
        keys_legend.append(k)
        vbar = np.array(v) + vbar
        height.append(np.array(v))
        colors_graph.append(colors[k])
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

    logger.info("numdata:" + str(numdata))
    logger.info("numbars: " + str(numbars))
    logger.info("sum_v: " + str(sum_v))

    left = np.array([i for i in range(numbars)])
    hbar = [0,]  # y軸メモリ位置
    hbar_labels = ["¥0", ]  # y軸メモリ見出し
    for i in sorted(vbar):
        hbar.append(i)
        hbar_labels.append(money.convert_yen(i))

    # create figure
    fig = plt.figure(figid, figsize=figsize)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.125, bottom=0.085, right=0.95, top=0.95, wspace=0.05, hspace=0.05)

    # bar
    bars = list()  # 凡例作成のため、リスト化
    for i in range(0, numdata):
        if i == 0:
            bars.append(ax.bar(left, height[i], color=colors_graph[i]))
            bottom = np.array(height[i])
        else:
            bars.append(ax.bar(left, height[i], bottom=bottom, color=colors_graph[i]))
            bottom = np.array(height[i] + bottom)
        for j in range(numbars):
            left_position1 = left_positions[numbars * i + j]
            label_position1 = label_positions[numbars * i + j]
            label1 = labels[numbars * i + j]
            ax.text(left_position1, label_position1, label1,
                    horizontalalignment='center',
                    verticalalignment='center'
                    )
    # legend
    ax.legend(bars, keys_legend, loc="best", prop=prop)
    # axis
    ax.set_xticks([i for i in range(numbars)])
    ax.set_xticklabels(vbar_labels, fontsize='small', fontproperties=prop)
    ax.set_yticks(hbar)
    ax.set_yticklabels(hbar_labels, fontsize='small', fontproperties=prop)
    ax.set_title(figtitle, fontproperties=prop)
    ax.yaxis.grid()
    [spine.set_visible(False) for spine in ax.spines.values()]
    # return response-data
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response


def fig_bars_basic(data={}, vbar_labels = [], figtitle="", figsize=(8, 8), figid=4):
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

    height = list()  # データ
    numdata = data.__len__()  # データ個数
    keys_legend = list()  # データ名
    labels = list()  # データラベル
    label_positions = list()  # labelのy位置
    left_positions = list()  # labelのx位置
    vbar = 0
    for k, v in data.items():
        if vbar is 0:
            numbars = v.__len__()  # 棒の数
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

    logger.info("numdata:" + str(numdata))
    logger.info("numbars: " + str(numbars))
    logger.info("sum_v: " + str(sum_v))

    left = np.array([i for i in range(numbars)])
    hbar = [0,]  # y軸メモリ位置
    hbar_labels = ["¥0", ]  # y軸メモリ見出し
    for i in sorted(vbar):
        hbar.append(i)
        hbar_labels.append(money.convert_yen(i))

    # create figure
    fig = plt.figure(figid, figsize=figsize)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.125, bottom=0.085, right=0.95, top=0.95, wspace=0.05, hspace=0.05)

    # bar
    bars = list()  # 凡例作成のため、リスト化
    for i in range(0, numdata):
        if i == 0:
            bars.append(ax.bar(left, height[i]))
            bottom = np.array(height[i])
        else:
            bars.append(ax.bar(left, height[i], bottom=bottom))
            bottom = np.array(height[i] + bottom)
        for j in range(numbars):
            left_position1 = left_positions[numbars * i + j]
            label_position1 = label_positions[numbars * i + j]
            label1 = labels[numbars * i + j]
            ax.text(left_position1, label_position1, label1,
                    horizontalalignment='center',
                    verticalalignment='center'
                    )
    # legend
    ax.legend(bars, keys_legend, loc="best", prop=prop)
    # axis
    ax.set_xticks([i for i in range(numbars)])
    ax.set_xticklabels(vbar_labels, fontsize='small', fontproperties=prop)
    ax.set_yticks(hbar)
    ax.set_yticklabels(hbar_labels, fontsize='small', fontproperties=prop)
    ax.set_title(figtitle, fontproperties=prop)
    ax.yaxis.grid()
    [spine.set_visible(False) for spine in ax.spines.values()]
    # return response-data
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response


# 線/点線/棒グラフ
def fig_barline_basic(left_bar=list(), height_bar=list(), label_bar="",
                      left_line=list(), height_line=list(), label_line="",
                      left_dot=list(), height_dot=list(), label_dot="",
                      xlabel="", xlim=list(), xticklabel=list(),
                      ylabel="", ylim=list(), yticklabel=list(),
                      figsize=(8,8), figid=5, figtitle="", width_bar=0.4):

    # lim
    if not xlim:
        xlim = [min(left_bar+left_line+left_dot), max(left_bar+left_line+left_dot)]
    if not ylim:
        ylim = [min(height_bar+height_line+height_dot), max(height_bar+height_line+height_dot)]

    # create figure
    fig = plt.figure(figid, figsize=figsize)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.125, bottom=0.085, right=0.95, top=0.95, wspace=0.05, hspace=0.05)

    # Bar
    if label_bar:
        left_bar = np.array(left_bar)
        height_bar = np.array(height_bar)
        ax.bar(left_bar, height_bar, color="blue", width=width_bar, label=label_bar)
    # Line
    if label_line:
        left_line = np.array(left_line)
        height_line = np.array(height_line)
        ax.plot(left_line, height_line, '-', color="red", label=label_line)

    # Prediction: dot-line
    if label_dot:
        height_dot = np.array(height_dot)
        left_dot = np.array(left_dot)
        ax.plot(left_dot, height_dot, '--', color="black", label=label_dot)

    # legend
    ax.legend(prop=prop)

    # axis, title
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if figtitle:
        ax.set_title(figtitle, fontproperties=prop)

    if xticklabel:
        ax.set_xticks(xlim)
        ax.set_xticklabels(xticklabel)
    else:
        ax.set_xlim(xlim)
    if yticklabel:
        ax.set_yticks(ylim)
        ax.set_yticklabels(yticklabel)
    else:
        ax.set_ylim(ylim)
    ax.grid()
    [spine.set_visible(False) for spine in ax.spines.values()]
    # return fig
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response


# 線グラフ
def fig_lines_basic(lefts=list(), heights=list(), labels=list(), colors=list(),
                      xlabel="", xlim=list(), xticklabel=list(),
                      ylabel="", ylim=list(), yticklabel=list(),
                      figsize=(8,8), figid=6, figtitle="",):
    # # test data
    # lefts = [
    #     [i for i in range(0, 11)],
    #     [j for j in range(10, 20)],
    # ]
    # heights = [
    #     [i for i in range(0, 11)],
    #     [10+10*j-j*j for j in range(0, 10)],
    # ]
    # labels = ["test1", "test2"]
    # colors = ["red", "blue"]
    # lim
    if not xlim:
        xlim = [min(itertools.chain(*lefts)), max(itertools.chain(*lefts))]
        logger.info((xlim))
    if not ylim:
        ylim = [min(itertools.chain(*heights)), max(itertools.chain(*heights))]
        logger.info(ylim)

    # create figure
    fig = plt.figure(figid, figsize=figsize)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.125, bottom=0.085, right=0.95, top=0.95, wspace=0.05, hspace=0.05)
    # Line
    for left, height, label, color in zip(lefts, heights, labels, colors):
        left_line = np.array(left)
        height_line = np.array(height)
        ax.plot(left_line, height_line, '-', color=color, label=label)

    # legend
    ax.legend(prop=prop)

    # axis, title
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if figtitle:
        ax.set_title(figtitle, fontproperties=prop)

    if xticklabel:
        ax.set_xticks(xlim)
        ax.set_xticklabels(xticklabel)
    else:
        ax.set_xlim(xlim)
    if yticklabel:
        ax.set_yticks(ylim)
        ax.set_yticklabels(yticklabel)
    else:
        ax.set_ylim(ylim)
    ax.grid()

    # return fig
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    fig.clear()
    return response
