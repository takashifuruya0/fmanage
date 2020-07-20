from django_pandas.io import read_frame
import logging
logger = logging.getLogger('django')


def prepare(svds):
    df = read_frame(svds)
    df['code'] = svds.first().stock.code if svds.exists() else None
    # 終値前日比, 出来高前日比
    df['val_close_dy'] = -(df['val_close'].shift() - df['val_close'])
    df['val_close_dy_pct'] = df['val_close_dy'] / df['val_close'].shift()
    df['turnover_dy'] = -(df['turnover'].shift() - df['turnover'])
    df['turnover_dy_pct'] = df['turnover_dy'] / df['turnover'].shift()
    # 終値-始値
    df['val_line'] = abs(df['val_close'] - df['val_open'])
    df['val_line_pct'] = (df['val_line'] / (df["val_high"] - df["val_low"])).where(df["val_line"] > 0, 0)
    # 陽線/陰線
    df['is_positive'] = False
    df['is_positive'] = df['is_positive'].where(df['val_close'] < df['val_open'], True)
    # 下ひげ/上ひげ
    df['lower_mustache'] = (df['val_open'] - df['val_low']).where(df['is_positive'], df['val_close'] - df['val_low'])
    df['upper_mustache'] = (df['val_high'] - df['val_close']).where(df['is_positive'], df['val_high'] - df['val_open'])
    # 移動平均
    df['ma05'] = df.val_close.rolling(window=5, min_periods=1).mean()
    df['ma25'] = df.val_close.rolling(window=25, min_periods=1).mean()
    df['ma75'] = df.val_close.rolling(window=75, min_periods=1).mean()
    # df['ma_diff5_25'] = df.ma05 - df.ma25
    # df['ma_diff5_25_pct'] = df.ma_diff5_25 / df.ma75
    # df['ma_diff25_75'] = df.ma25 - df.ma75
    # df['ma_diff25_75_pct'] = df.ma_diff25_75 / df.ma75
    df['ma05_diff'] = df.val_close - df.ma05
    df['ma05_diff_pct'] = df['ma05_diff'] / df.val_close
    df['ma25_diff'] = df.val_close - df.ma25
    df['ma25_diff_pct'] = df['ma25_diff'] / df.val_close
    df['ma75_diff'] = df.val_close - df.ma75
    df['ma75_diff_pct'] = df['ma75_diff'] / df.val_close
    # ボリンジャーバンド（25日）
    df["sigma25"] = df.val_close.rolling(window=25).std()
    df["ma25_p2sigma"] = df.ma25 + 2 * df.sigma25
    df["ma25_m2sigma"] = df.ma25 - 2 * df.sigma25
    # trend
    df['is_upper05'] = False
    df['is_upper05'] = df['is_upper05'].where(df['ma05'].diff() < 0, True)
    df['is_upper25'] = False
    df['is_upper25'] = df['is_upper25'].where(df['ma25'].diff() < 0, True)
    df['is_upper75'] = False
    df['is_upper75'] = df['is_upper75'].where(df['ma75'].diff() < 0, True)
    # return
    return df


def get_trend(df):
    try:
        df_reverse = df.sort_values('date', ascending=False)
        logger.info("len(df_reverse) {}".format(len(df_reverse)))
        ma05 = df_reverse['ma05']
        ma25 = df_reverse['ma25']
        ma75 = df_reverse['ma75']
        res = dict()
        # 5
        trend_period_5 = 1
        if len(ma05) > 2 and ma05.iloc[0] > ma05.iloc[1]:
            res['is_upper05'] = True
            for i in range(2, len(df_reverse)):
                if ma05.iloc[i - 1] > ma05.iloc[i]:
                    trend_period_5 += 1
                else:
                    break
        elif len(ma05) > 2 and ma05.iloc[0] < ma05.iloc[1]:
            res['is_upper05'] = False
            for i in range(2, len(df_reverse)):
                if ma05.iloc[i - 1] < ma05.iloc[i]:
                    trend_period_5 += 1
                else:
                    break
        # 25
        trend_period_25 = 1
        if len(ma25) > 2 and ma25.iloc[0] > ma25.iloc[1]:
            res['is_upper25'] = True
            for i in range(2, len(df_reverse)):
                if ma25.iloc[i-1] > ma25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        elif len(ma25) > 2 and ma25.iloc[0] < ma25.iloc[1]:
            res['is_upper25'] = False
            for i in range(2, len(df_reverse)):
                if ma25.iloc[i-1] < ma25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        # 75
        trend_period_75 = 1
        if len(ma75) > 2 and ma75.iloc[0] > ma75.iloc[1]:
            res['is_upper75'] = True
            for i in range(2, len(df_reverse)):
                if ma75.iloc[i-1] > ma75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break
        elif len(ma75) > 2 and ma75.iloc[0] < ma75.iloc[1]:
            res['is_upper75'] = False
            for i in range(2, len(df_reverse)):
                if ma75.iloc[i-1] < ma75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break
        # res
        res['period_5'] = trend_period_5
        res['period_25'] = trend_period_25
        res['period_75'] = trend_period_75

    except Exception as e:
        logger.error("get_trend was failed")
        logger.error(e)
        logger.error("ma05: {}".format(ma05))
        logger.error("ma25: {}".format(ma25))
        logger.error("ma75: {}".format(ma75))
        logger.error("df_reverse {}".format(df_reverse))
        res = {
            "is_upper05": None,
            "period_5": None,
            "is_upper25": None,
            "period_25": None,
            "is_upper75": None,
            "period_75": None,
        }
    finally:
        return res


def check(df):
    try:
        trend = get_trend(df)
        df_reverse = df.sort_values('date', ascending=False)
        data = list()
        for i in range(len(df_reverse)-4):
            # たくり線
            check_name = "たくり線"
            if df_reverse.iloc[i]['lower_mustache'] > 2 * df_reverse.iloc[i]['upper_mustache'] \
                    and df_reverse.iloc[i]['lower_mustache'] > 2 * df_reverse.iloc[i]['val_line'] \
                    and not trend['is_upper25'] and trend['period_25'] > 2:
                msg = "たくり線：底" \
                      + "（ヒゲ：" + str(df_reverse.iloc[i]['lower_mustache']) \
                      + " / 線：" + str(df_reverse.iloc[i]['val_line']) \
                      + "）"
                # data["たくり線_底"].append(df_reverse.iloc[i])
                data.append({
                    "type": "たくり線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
                logger.info("{}: {}".format(df_reverse.iloc[i]['date'], msg))
            # 包線:　当日の線[i]が、前日の線[i+1]を包みこむ
            check_name = "包線"
            if not df_reverse.iloc[i+1]['is_positive'] and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_close']:
                # 陰線→陽線
                if trend['is_upper25'] and trend['period_25'] > 2:
                    # 上昇傾向→天井
                    msg = "包み陽線：天井（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_天井'].append(df_reverse.iloc[i])
                    data.append({
                        # "type": "包線（陰→陽＠上昇）",
                        "type": "包線",
                        "is_bottom": False,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
                elif not trend['is_upper25'] and trend['period_25'] > 2:
                    # 下落傾向→底
                    msg = "包み陽線：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_底'].append(df_reverse.iloc[i])
                    data.append({
                        # "type": "包線（陰→陽＠下降）",
                        "type": "包線",
                        "is_bottom": True,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
            elif df_reverse.iloc[i+1]['is_positive'] and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_close'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_open'] > df_reverse.iloc[i]['val_close']:
                # 陽線→陰線
                if trend['is_upper25'] and trend['period_25'] > 2:
                    # 上昇傾向→天井
                    msg = "包み陰線：天井（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_天井'].append(df_reverse.iloc[i])
                    data.append({
                        # "type": "包線（陽→陰＠上昇）",
                        "type": "包線",
                        "is_bottom": False,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
                elif not trend['is_upper25'] and trend['period_25'] > 2:
                    # 下落傾向→底
                    msg = "包み陰線：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_底'].append(df_reverse.iloc[i])
                    data.append({
                        # "type": "包線（陽→陰＠下降）",
                        "type": "包線",
                        "is_bottom": True,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
            # 2. はらみ線
            check_name = "はらみ線"
            if not df_reverse.iloc[i+1]['is_positive'] \
                    and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_close'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_open'] > df_reverse.iloc[i]['val_close'] \
                    and trend['is_upper25'] and trend['period_25'] > 2:
                # 陰の陽はらみ
                msg = "陰の陽はらみ：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                # data['はらみ線_底'].append(df_reverse.iloc[i])
                logger.info(msg)
                data.append({
                    # "type": "はらみ線（陰→陽＠上昇）",
                    "type": "はらみ線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            elif not df_reverse.iloc[i+1]['is_positive'] \
                    and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_close'] \
                    and trend['is_upper25'] and trend['period_25'] > 2:
                # 陰の陰はらみ
                msg = "陰の陰はらみ：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                # data['はらみ線_底'].append(df_reverse.iloc[i])
                logger.info(msg)
                data.append({
                    # "type": "はらみ線（陰→陰＠上昇）",
                    "type": "はらみ線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            elif df_reverse.iloc[i+1]['is_positive'] \
                    and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_close'] \
                    and not trend['is_upper25'] and trend['period_25'] > 2:
                # 陽の陽はらみ
                msg = "陽の陽はらみ：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                # data['はらみ線_底'].append(df_reverse.iloc[i])
                logger.info(msg)
                data.append({
                    "type": "はらみ線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            elif df_reverse.iloc[i+1]['is_positive'] \
                    and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_close'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_open'] \
                    and not trend['is_upper25'] and trend['period_25'] > 2:
                # 陽の陰はらみ
                msg = "陰の陰はらみ：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                # data['はらみ線_底'].append(df_reverse.iloc[i])
                logger.info(msg)
                data.append({
                    "type": "はらみ線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            # 3. 上げ三法: 1本目の安値を割り込まない, 4本目が1本目の終値を超える
            check_name = "上げ三法"
            if df_reverse.iloc[i+4]["is_positive"] \
                    and not df_reverse.iloc[i+3]['is_positive'] \
                    and not df_reverse.iloc[i+2]['is_positive'] \
                    and not df_reverse.iloc[i+1]['is_positive'] \
                    and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i]['val_close'] \
                    > df_reverse.iloc[i+4]['val_close'] \
                    > df_reverse.iloc[i+3]['val_open'] \
                    > df_reverse.iloc[i+2]['val_open'] \
                    > df_reverse.iloc[i+1]['val_open'] \
                    and df_reverse.iloc[i+4]['val_open'] \
                    < df_reverse.iloc[i+1]['val_close'] \
                    < df_reverse.iloc[i+2]['val_close'] \
                    < df_reverse.iloc[i+3]['val_close']:
                logger.info("上げ三法：◯")
                # data['上げ三法_底'].append(df_reverse.iloc[i])
                data.append({
                    "type": "上げ三法",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            # 4. 三空叩き込み
            check_name = "三空叩き込み"
            if not df_reverse.iloc[i+3]['is_positive'] and not df_reverse.iloc[i+2]['is_positive'] \
                    and not df_reverse.iloc[i+1]['is_positive'] and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+3]['val_open'] < df_reverse.iloc[i+2]['val_close'] \
                    and df_reverse.iloc[i+2]['val_open'] < df_reverse.iloc[i+1]['val_close'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_close']:
                logger.info("三空叩き込み：◯")
                # data['三空叩き込み_底'].append(df_reverse.iloc[i])
                data.append({
                    "type": "三空叩き込み",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            # 5. 三手大陰線
            check_name = "三手大陰線"
            if not df_reverse.iloc[i+2]['is_positive'] \
                    and not df_reverse.iloc[i+1]['is_positive'] \
                    and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+2]['val_line'] / df_reverse.iloc[i+2]['val_close'] > 0.05 \
                    and df_reverse.iloc[i+1]['val_line'] / df_reverse.iloc[i+1]['val_close'] > 0.05 \
                    and df_reverse.iloc[i]['val_line'] / df_reverse.iloc[i]['val_close'] > 0.05:
                logger.info("三手大陰線：◯")
                # data['三手大陰線_底'].append(df_reverse.iloc[i])
                data.append({
                    "type": "三手大陰線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            # 6. 下げ三法: 1本目の高値を割り込まない, 4本目が1本目の終値を下回る
            check_name = "下げ三法"
            if not df_reverse.iloc[i + 4]["is_positive"] \
                    and df_reverse.iloc[i + 3]['is_positive'] \
                    and df_reverse.iloc[i + 2]['is_positive'] \
                    and df_reverse.iloc[i + 1]['is_positive'] \
                    and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i]['val_close'] \
                    < df_reverse.iloc[i + 4]['val_close'] \
                    < df_reverse.iloc[i + 3]['val_open'] \
                    < df_reverse.iloc[i + 2]['val_open'] \
                    < df_reverse.iloc[i + 1]['val_open'] \
                    and df_reverse.iloc[i + 4]['val_open'] \
                    > df_reverse.iloc[i + 1]['val_close'] \
                    > df_reverse.iloc[i + 2]['val_close'] \
                    > df_reverse.iloc[i + 3]['val_close']:
                logger.info("下げ三法：◯")
                # data['上げ三法_底'].append(df_reverse.iloc[i])
                data.append({
                    "type": "下げ三法",
                    "is_bottom": False,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
    except Exception as e:
        logger.error("({}) {}: {}".format(i, check_name, e))
    finally:
        return data


def test():
    from web.models import StockValueData
    svds = StockValueData.objects.filter(stock__code=6460).order_by('date')
    df = prepare(svds)
    return df
