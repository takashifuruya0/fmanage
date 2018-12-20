from django.shortcuts import render, HttpResponse, Http404, redirect
from django.contrib import messages
import logging
logger = logging.getLogger("django")
from django.db.models.functions import Length
from datetime import date
from kakeibo.functions.mylib import time_measure
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders, StockDataByDate
from asset.functions import get_info, mylib_asset, analysis_asset
from asset.forms import AddInvestmentForm, OrdersForm, StocksForm
# Template-view
from django.views.generic.edit import CreateView
# login
from django.contrib.auth.decorators import login_required
# pandas
from django_pandas.io import read_frame


# 概要
@login_required
@time_measure
def asset_dashboard(request):
    today = date.today()

    # FormのPost処理
    if request.method == "POST":
        logger.info(request.POST)
        # Add investment
        if request.POST['post_type'] == "add_investment":
            try:
                form = AddInvestmentForm(request.POST)
                form.is_valid()
                post_data = form.cleaned_data
                # 今日のastatusを取得。無い場合は新規作成
                astatus_today = AssetStatus.objects.filter(date=today)
                if astatus_today:
                    astatus = astatus_today[0]
                else:
                    astatus = AssetStatus.objects.all().order_by('date').last()
                    astatus.pk = None
                    astatus.date = today
                astatus.investment += post_data.get('value')
                astatus.buying_power += post_data.get('value')
                astatus.total += + post_data.get('value')
                astatus.save()
                smsg = "Additional investment was registered: " + str(post_data.get('value'))
                messages.success(request, smsg)
                logger.info(smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)
                messages.error(request, emsg)
            finally:
                return redirect('asset:dashboard')
        # Stock
        elif request.POST['post_type'] == "stock_form":
            try:
                form = StocksForm(request.POST)
                form.is_valid()
                post_data = form.cleaned_data
                stock = Stocks()
                stock.code = post_data.get('code')
                stock.name = get_info.stock_overview(stock.code)['name']
                stock.save()
                # kabuoji3よりデータ取得
                if len(stock.code) > 4:
                    # 投資信託
                    pass
                else:
                    # 株
                    data = get_info.kabuoji3(stock.code)
                    if data['status']:
                        # 取得成功時
                        for d in data['data']:
                            # (date, stock)の組み合わせでデータがなければ追加
                            if StockDataByDate.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                                sdbd = StockDataByDate()
                                sdbd.stock = stock
                                sdbd.date = d[0]
                                sdbd.val_start = d[1]
                                sdbd.val_high = d[2]
                                sdbd.val_low = d[3]
                                sdbd.val_end = d[4]
                                sdbd.turnover = d[5]
                                sdbd.save()
                        logger.info('StockDataByDate of "%s" are updated' % stock.code)
                    else:
                        # 取得失敗時
                        logger.error(data['msg'])
                smsg = "New stock was registered:" + str(post_data.get('code'))
                messages.success(request, smsg)
                logger.info(smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)
                messages.error(request, emsg)
            finally:
                return redirect('asset:dashboard')
        # Order
        elif request.POST['post_type'] == "order_form":
            try:
                form = OrdersForm(request.POST)
                form.is_valid()
                post_data = form.cleaned_data
                order = Orders()
                order.datetime = post_data.get('datetime')
                order.order_type = post_data.get('order_type')
                order.stock = post_data.get('stock')
                order.num = post_data.get('num')
                if len(order.stock.code) == 4:
                    # 株
                    order.price = post_data.get('price')
                    order.commission = mylib_asset.get_commission(order.num * order.price) if order.is_nisa else 0
                else:
                    # 投資信託
                    order.price = float(post_data.get('price')) / 10000
                    order.commission = 0
                order.is_nisa = post_data.get('is_nisa')
                order.save()
                # order時の共通プロセス
                smsg, emsg = mylib_asset.order_process(order)
                if emsg:
                    raise ValueError(emsg)
                else:
                    logger.info(smsg)
                    smsg = "New order was registered"
                    logger.info(smsg)
                    messages.success(request, smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)
                messages.error(request, emsg)
            finally:
                return redirect('asset:dashboard')

    # Form
    stock_form = StocksForm()
    order_form = OrdersForm()
    add_investment_form = AddInvestmentForm()

    # 保有株リスト：現在値で登録
    holdings = {
        "all": list(),
        "trust": list(),
        "stock":  list(),
    }
    hss = HoldingStocks.objects.all().select_related('stock')
    for hs in hss:
        current_price = hs.get_current_price()
        current_total = current_price * hs.num
        benefit = (current_price - hs.price) * hs.num
        res = {
            "date": hs.date,
            "name": hs.stock.name,
            "code": hs.stock.code,
            "num": hs.num,
            "price": hs.price,
            "total": hs.price * hs.num,
            "current_price": current_price,
            "current_total": current_total,
            "benefit": benefit,
            "color": mylib_asset.val_color(benefit),
        }
        holdings['all'].append(res)
        if len(hs.stock.code) == 4:
            holdings['stock'].append(res)
        else:
            res["price"] = hs.price * 10000
            res["current_price"] = current_price * 10000
            holdings['trust'].append(res)

    # 総資産
    current_benefit = mylib_asset.get_benefit_all()

    # ステータス
    astatus = AssetStatus.objects.all().order_by('date')
    try:
        astatus_recent = astatus[len(astatus) - 15:len(astatus)]
    except Exception as e:
        logger.error(e)
        astatus_recent = None

    # 現在のトータル
    total = astatus.last().buying_power + current_benefit['total_all']
    # 最近のorder
    orders = Orders.objects.all().order_by('-datetime')[:10]

    # return
    output = {
        "today": today,
        "holdings": holdings,
        "current_benefit": current_benefit,
        "order_form": order_form,
        "stock_form": stock_form,
        "add_investment_form": add_investment_form,
        "total_color": mylib_asset.val_color(current_benefit['benefit_all']),
        "total": total,
        "astatus": astatus,
        "astatus_recent": astatus_recent,
        "orders": orders,
    }
    return render(request, 'asset/adashboard.html', output)


class StocksCreateView(CreateView):
    model = Stocks
    fields = ("code", "name")  # リストもしくはタプル


class HoldingStocksCreateView(CreateView):
    model = HoldingStocks
    fields = ("stock", "date", "price", "num")  # リストもしくはタプル


class OrdersCreateView(CreateView):
    model = Orders
    fields = ("datetime", "order_type", "stock", "num", "price", "commission", "is_nisa")


def ajax(request):
    if request.method == 'POST':
        # response = json.dumps({'your_surprise_txt': "surprise_txt" })  # JSON形式に直して・・
        # return HttpResponse(response, content_type="text/javascript")  # 返す。JSONはjavascript扱いなのか・・
        name = get_info.stock_overview(request.POST['code'])['name']
        return HttpResponse(name)
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも


@login_required
@time_measure
def analysis_list(request):
    stocks = dict()
    for stock in Stocks.objects.annotate(code_len=Length('code')).filter(code_len=4):
        sdbd_ascending = StockDataByDate.objects.filter(stock=stock).order_by('date')
        # sdbdがないstockはスキップ
        if sdbd_ascending.__len__() > 0:
            df_ascending = analysis_asset.analyse_stock_data(read_frame(sdbd_ascending))
            # トレンドを取得
            trend = analysis_asset.get_trend(df_ascending)
            # トレンド転換マークをチェック
            mark = analysis_asset.check_mark(df_ascending)
            # 最新データである最後尾を取得
            df_latest = df_ascending.tail(1)
            stocks[stock.code] = {
                "name": stock.name,
                "val_end": df_latest.val_end,
                "val_end_diff_percent": float(df_latest.val_end_diff_percent),
                "turnover": df_latest.turnover,
                "turnover_diff_percent": float(df_latest.turnover_diff_percent),
                "mark": mark,
                "trend": trend,
            }
    # for stock in stocks:
    output = {
        "stocks": stocks,
    }
    return render(request, 'asset/analysis_list.html', output)


@login_required
@time_measure
def analysis_detail(request, code):
    length = request.GET.get(key='length', default=None)
    if len(code) > 4:
        return redirect("asset:analysis_list")
    else:
        stock = Stocks.objects.get(code=code)
        sdbds_ascending = StockDataByDate.objects.filter(stock__code=code).order_by('date')
        df_ascending = analysis_asset.analyse_stock_data(read_frame(sdbds_ascending))
        # trend
        trend = analysis_asset.get_trend(df_ascending)
        # length指定ありの場合
        if length:
            df_ascending = df_ascending.tail(int(length))
        # GOLDEN CROSS / DEAD CROSS
        cross = analysis_asset.get_cross(df_ascending)
        # order
        order_points = analysis_asset.get_order_point(df_ascending)
        # mark
        mark = analysis_asset.check_mark(df_ascending)
        # 逆向き
        df_ascending_reverse = df_ascending.sort_values('date', ascending=False)
        # 直近
        df_recent = df_ascending_reverse.iloc[0]
        # return
        output = {
            "stock": stock,
            "df_ascending": df_ascending,
            "df_ascending_reverse": df_ascending_reverse,
            "df_recent": df_recent,
            "mark": mark,
            "cross": cross,
            "length": length,
            "trend": trend,
            "order_points": order_points,
        }
        return render(request, 'asset/analysis_detail.html', output)
