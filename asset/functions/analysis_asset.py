import logging
logger = logging.getLogger("django")
from asset.models import Orders


def analyse_stock_data(df_ascending):
    # 終値前日比, 出来高前日比
    df_ascending['val_end_diff'] = -(df_ascending['val_end'].shift() - df_ascending['val_end'])
    df_ascending['val_end_diff_percent'] = round(-(df_ascending['val_end'].shift() - df_ascending['val_end']) / df_ascending['val_end'].shift() * 100, 1)
    df_ascending['turnover_diff'] = -(df_ascending['turnover'].shift() - df_ascending['turnover'])
    df_ascending['turnover_diff_percent'] = round(-(df_ascending['turnover'].shift() - df_ascending['turnover']) / df_ascending['turnover'].shift() * 100, 1)
    # 終値-始値
    df_ascending['val_end-start'] = df_ascending['val_end'] - df_ascending['val_start']
    # 陽線/陰線
    df_ascending['is_positive'] = False
    df_ascending['is_positive'] = df_ascending['is_positive'].where(df_ascending['val_end-start'] < 0, True)
    # 下ひげ
    df_ascending['lower_mustache'] = (df_ascending['val_start'] - df_ascending['val_low']).where(df_ascending['is_positive'], df_ascending['val_end'] - df_ascending['val_low'])
    # 上ひげ
    df_ascending['upper_mustache'] = (df_ascending['val_high'] - df_ascending['val_end']).where(df_ascending['is_positive'], df_ascending['val_high'] - df_ascending['val_start'])
    # 移動平均
    df_ascending['ma_5'] = df_ascending.val_end.rolling(window=5, min_periods=1).mean()
    df_ascending['ma_25'] = df_ascending.val_end.rolling(window=25, min_periods=1).mean()
    df_ascending['ma_75'] = df_ascending.val_end.rolling(window=75, min_periods=1).mean()
    df_ascending['ma_diff'] = df_ascending.ma_25 - df_ascending.ma_75
    # ボリンジャーバンド（25日）
    df_ascending["sigma_25"] = df_ascending.val_end.rolling(window=25).std()
    df_ascending["ma_25p2sigma"] = df_ascending.ma_25 + 2 * df_ascending.sigma_25
    df_ascending["ma_25m2sigma"] = df_ascending.ma_25 - 2 * df_ascending.sigma_25

    return df_ascending


def get_cross(df_ascending):
    try:
        # nanを含む列は除外
        df = df_ascending.dropna()
        cross = {
            "golden": [None, ],
            "dead": [None, ],
            "recent_golden": None,
            "recent_dead": None,
        }
        for i in range(1, len(df)):
            if df.iloc[i - 1]['ma_diff'] < 0 and df.iloc[i]['ma_diff'] > 0:
                logger.info("{}:GOLDEN CROSS".format(df.iloc[i]["date"]))
                cross['golden'].append(df.iloc[i]['ma_25'])
                cross['dead'].append(None)
                cross['recent_golden'] = df.iloc[i]["date"]
            elif df.iloc[i - 1]['ma_diff'] > 0 and df.iloc[i]['ma_diff'] < 0:
                logger.info("{}:DEAD CROSS".format(df.iloc[i]["date"]))
                cross['golden'].append(None)
                cross['dead'].append(df.iloc[i]['ma_25'])
                cross['recent_dead'] = df.iloc[i]["date"]
            else:
                cross['golden'].append(None)
                cross['dead'].append(None)
    except Exception as e:
        logger.error("get_cross was failed")
        logger.error(e)
        cross = {
            "golden": [None for i in range(len(df))],
            "dead": [None for i in range(len(df))],
            "recent_golden": None,
            "recent_dead": None,
        }
    finally:
        return cross


def get_order_point(df_ascending):
    try:
        # nanを含む列は除外
        df = df_ascending.dropna()
        orders = Orders.objects.filter(stock__code=df_ascending.iloc[0].stock[0:4])
        orders_date = [o.datetime.date() for o in orders]

        order_point = {
            "buy": list(),
            "sell": list(),
            "num_buy": 0,
            "num_sell": 0,
            "orders_date": orders_date
        }

        for i in range(len(df)):
            if df.iloc[i].date in orders_date:
                buys = orders.filter(datetime__date=df.iloc[i].date, order_type='現物買')
                if buys:
                    price = sum(b.price*b.num for b in buys)/sum(b.num for b in buys)
                    order_point['buy'].append(round(price, 0))
                    order_point["num_buy"] += 1
                else:
                    order_point['sell'].append(None)
                sells = orders.filter(datetime__date=df.iloc[i].date, order_type='現物売')
                if sells:
                    price = sum(s.price * s.num for s in sells) / sum(s.num for s in sells)
                    order_point['sell'].append(round(price, 0))
                    order_point["num_sell"] += 1
                else:
                    order_point['sell'].append(None)
            else:
                order_point['buy'].append(None)
                order_point['sell'].append(None)
    except Exception as e:
        logger.error("get_order_point was failed")
        logger.error(e)
        order_point = {
            "buy": [None for i in range(len(df))],
            "sell": [None for i in range(len(df))],
            "num_buy": 0,
            "num_sell": 0,
            "orders_date": orders_date
        }
    finally:
        return order_point


def check_mark(df_ascending):
    try:
        # mark
        mark = list()
        df_ascending_reverse = df_ascending.sort_values('date', ascending=False)
        # トレンド
        trend = get_trend(df_ascending)
        # 陽線・陰線の長さ
        bar1 = abs(df_ascending_reverse.iloc[1]['val_end-start'])
        bar0 = abs(df_ascending_reverse.iloc[0]['val_end-start'])

        # 0. たくり線・勢力線// 前日にカラカサか下影陰線→◯。3日前~2日前で陰線だったら◎
        if df_ascending_reverse.iloc[0]['lower_mustache'] > 2*df_ascending_reverse.iloc[0]['upper_mustache'] \
                and not trend['is_upper_25'] and trend['period_25'] > 2:
            msg = "たくり線：底" \
                  + "（ヒゲ：" + str(df_ascending_reverse.iloc[0]['lower_mustache']) \
                  + " / 線：" + str(abs(df_ascending_reverse.iloc[0]['val_end-start'])) \
                  + "）"
            mark.append(msg)
            logger.info(msg)

        else:
            mark.append("")

        # 1. 包線
        if not df_ascending_reverse.iloc[1]['is_positive'] and df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[1]['val_end'] > df_ascending_reverse.iloc[0]['val_start'] \
                and df_ascending_reverse.iloc[1]['val_start'] < df_ascending_reverse.iloc[0]['val_end']:
            # 陰線→陽線
            if trend['is_upper_25'] and trend['period_25'] > 2:
                # 上昇傾向→天井
                msg = "包み陽線：天井（" + str(bar1) + "→" + str(bar0) + "）"
                mark.append(msg)
                logger.info(msg)
            elif not trend['is_upper_25'] and trend['period_25'] > 2:
                # 下落傾向→底
                msg = "包み陽線：底（" + str(bar1) + "→" + str(bar0) + "）"
                mark.append(msg)
                logger.info(msg)
            else:
                # 傾向なし
                mark.append("")
        elif df_ascending_reverse.iloc[1]['is_positive'] and not df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[1]['val_end'] < df_ascending_reverse.iloc[0]['val_start'] \
                and df_ascending_reverse.iloc[1]['val_start'] > df_ascending_reverse.iloc[0]['val_end']:
            # 陽線→陰線
            if trend['is_upper_25'] and trend['period_25'] > 2:
                # 上昇傾向→天井
                msg = "包み陰線：天井（" + str(bar1) + "→" + str(bar0) + "）"
                mark.append(msg)
                logger.info(msg)
            elif not trend['is_upper_25'] and trend['period_25'] > 2:
                # 下落傾向→底
                msg = "包み陰線：底（" + str(bar1) + "→" + str(bar0) + "）"
                mark.append(msg)
                logger.info(msg)
            else:
                # 傾向なし
                mark.append("")
        else:
            mark.append("")

        # 2. はらみ線
        if not df_ascending_reverse.iloc[1]['is_positive'] \
                and df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[1]['val_end'] < df_ascending_reverse.iloc[0]['val_start'] \
                and df_ascending_reverse.iloc[1]['val_start'] > df_ascending_reverse.iloc[0]['val_end'] \
                and trend['is_upper_25'] and trend['period_25'] > 2:
            # 陰の陽はらみ
            msg = "陰の陽はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            mark.append(msg)
            logger.info(msg)
        elif not df_ascending_reverse.iloc[1]['is_positive'] \
                and not df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[1]['val_start'] < df_ascending_reverse.iloc[0]['val_start'] \
                and df_ascending_reverse.iloc[1]['val_end'] > df_ascending_reverse.iloc[0]['val_end']\
                and trend['is_upper_25'] and trend['period_25'] > 2:
            # 陰の陰はらみ
            msg = "陰の陰はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            mark.append(msg)
            logger.info(msg)
        elif df_ascending_reverse.iloc[1]['is_positive'] \
                and df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[1]['val_start'] < df_ascending_reverse.iloc[0]['val_start'] \
                and df_ascending_reverse.iloc[1]['val_end'] > df_ascending_reverse.iloc[0]['val_end'] \
                and not trend['is_upper_25'] and trend['period_25'] > 2:
            # 陽の陽はらみ
            msg = "陽の陽はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            mark.append(msg)
            logger.info(msg)
        elif df_ascending_reverse.iloc[1]['is_positive'] \
                and not df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[1]['val_start'] < df_ascending_reverse.iloc[0]['val_end'] \
                and df_ascending_reverse.iloc[1]['val_end'] > df_ascending_reverse.iloc[0]['val_start'] \
                and not trend['is_upper_25'] and trend['period_25'] > 2:
            # 陽の陰はらみ
            msg = "陰の陰はらみ：底（" + str(bar1) + "→" + str(bar0) + "）"
            mark.append(msg)
            logger.info(msg)
        else:
            mark.append("")

        # 3. 上げ三法: 1本目の安値を割り込まない, 4本目が1本目の終値を超える
        if not df_ascending_reverse.iloc[3]['is_positive'] and not df_ascending_reverse.iloc[2]['is_positive'] \
                and not df_ascending_reverse.iloc[1]['is_positive'] and df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[3]['val_start'] > df_ascending_reverse.iloc[2]['val_start'] \
                and df_ascending_reverse.iloc[3]['val_start'] > df_ascending_reverse.iloc[1]['val_start'] \
                and df_ascending_reverse.iloc[1]['val_end'] < df_ascending_reverse.iloc[0]['val_start'] \
                and df_ascending_reverse.iloc[3]['val_start'] < df_ascending_reverse.iloc[0]['val_end']:
            mark.append("上げ三法：◯")
            logger.info("上げ三法：◯")
        else:
            mark.append("")

        # 4. 三空叩き込み
        if not df_ascending_reverse.iloc[3]['is_positive'] and not df_ascending_reverse.iloc[2]['is_positive'] \
                and not df_ascending_reverse.iloc[1]['is_positive'] and not df_ascending_reverse.iloc[0]['is_positive'] \
                and df_ascending_reverse.iloc[3]['val_start'] < df_ascending_reverse.iloc[2]['val_end'] \
                and df_ascending_reverse.iloc[2]['val_start'] < df_ascending_reverse.iloc[1]['val_end'] \
                and df_ascending_reverse.iloc[1]['val_start'] < df_ascending_reverse.iloc[0]['val_end']:
            mark.append("三空叩き込み：◯")
            logger.info("三空叩き込み：◯")
        else:
            mark.append("")

        # 5. 三手大陰線
        if not df_ascending_reverse.iloc[2]['is_positive'] and not df_ascending_reverse.iloc[1]['is_positive'] and not df_ascending_reverse.iloc[0]['is_positive'] \
                and -df_ascending_reverse.iloc[2]['val_end-start'] / df_ascending_reverse.iloc[2]['val_end'] > 0.05 \
                and -df_ascending_reverse.iloc[1]['val_end-start'] / df_ascending_reverse.iloc[1]['val_end'] > 0.05 \
                and -df_ascending_reverse.iloc[0]['val_end-start'] / df_ascending_reverse.iloc[0]['val_end'] > 0.05:
            mark.append("三手大陰線：◯")
            logger.info("三手大陰線：◯")
        else:
            mark.append("")
        # mark = ["◯" for i in range(mark.__len__())]
    except Exception as e:
        logger.error("check_mark was failed")
        logger.error(e)
        mark = ["" for i in range(5)]
    finally:
        return mark


def get_trend(df_ascending):
    try:
        df_ascending_reverse = df_ascending.sort_values('date', ascending=False)
        ma_25 = df_ascending_reverse['ma_25']
        ma_75 = df_ascending_reverse['ma_75']
        res = dict()
        trend_period_25 = 1
        trend_period_75 = 1

        if ma_25.iloc[0] > ma_25.iloc[1]:
            res['is_upper_25'] = True
            for i in range(2, len(df_ascending_reverse)):
                if ma_25.iloc[i-1] > ma_25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        elif ma_25.iloc[0] < ma_25.iloc[1]:
            res['is_upper_25'] = False
            for i in range(2, len(df_ascending_reverse)):
                if ma_25.iloc[i-1] < ma_25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break

        if ma_75.iloc[0] > ma_75.iloc[1]:
            res['is_upper_75'] = True
            for i in range(2, len(df_ascending_reverse)):
                if ma_75.iloc[i-1] > ma_75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break
        elif ma_75.iloc[0] < ma_75.iloc[1]:
            res['is_upper_75'] = False
            for i in range(2, len(df_ascending_reverse)):
                if ma_75.iloc[i-1] < ma_75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break

        res['period_25'] = trend_period_25
        res['period_75'] = trend_period_75

    except Exception as e:
        logger.error("get_trend was failed")
        logger.error(e)
        res = {
            "is_upper_25": None,
            "period_25": None,
            "is_upper_75": None,
            "period_75": None,
        }
    finally:
        return res
