from django_pandas.io import read_frame
import logging
logger = logging.getLogger('django')


def prepare(svds):
    df = read_frame(svds)
    df['code'] = svds.first().stock.code if svds.exists() else None
    # 終値前日比, 出来高前日比
    df['val_close_diff'] = -(df['val_close'].shift() - df['val_close'])
    df['val_close_diff_pct'] = df['val_close_diff'] / df['val_close'].shift()
    df['turnover_diff'] = -(df['turnover'].shift() - df['turnover'])
    df['turnover_diff_pct'] = df['turnover_diff'] / df['turnover'].shift()
    # 終値-始値
    df['val_close_open'] = df['val_close'] - df['val_open']
    df['val_line'] = abs(df['val_close_open'])
    df['val_line_pct'] = (df['val_line'] / (df["val_high"] - df["val_low"])).where(df["val_line"] > 0, None)
    # 陽線/陰線
    df['is_positive'] = False
    df['is_positive'] = df['is_positive'].where(df['val_close_open'] < 0, True)
    # 下ひげ/上ひげ
    df['lower_mustache'] = (df['val_open'] - df['val_low']).where(df['is_positive'], df['val_close'] - df['val_low'])
    df['upper_mustache'] = (df['val_high'] - df['val_close']).where(df['is_positive'], df['val_high'] - df['val_open'])
    # 移動平均
    df['ma_5'] = df.val_close.rolling(window=5, min_periods=1).mean()
    df['ma_25'] = df.val_close.rolling(window=25, min_periods=1).mean()
    df['ma_75'] = df.val_close.rolling(window=75, min_periods=1).mean()
    df['ma_diff5_25'] = df.ma_5 - df.ma_25
    df['ma_diff5_25_pct'] = df.ma_diff5_25 / df.ma_75
    df['ma_diff25_75'] = df.ma_25 - df.ma_75
    df['ma_diff25_75_pct'] = df.ma_diff25_75 / df.ma_75
    df['diff_ma_5'] = df.val_close - df.ma_5
    df['diff_ma_5_pct'] = df['diff_ma_5'] / df.val_close
    df['diff_ma_25'] = df.val_close - df.ma_25
    df['diff_ma_25_pct'] = df['diff_ma_25'] / df.val_close
    df['diff_ma_75'] = df.val_close - df.ma_75
    df['diff_ma_75_pct'] = df['diff_ma_75'] / df.val_close
    # ボリンジャーバンド（25日）
    df["sigma_25"] = df.val_close.rolling(window=25).std()
    df["ma_25p2sigma"] = df.ma_25 + 2 * df.sigma_25
    df["ma_25m2sigma"] = df.ma_25 - 2 * df.sigma_25
    # trend
    df['is_upper_5'] = False
    df['is_upper_5'] = df['is_upper_5'].where(df['ma_5'].diff() < 0, True)
    df['is_upper_25'] = False
    df['is_upper_25'] = df['is_upper_25'].where(df['ma_25'].diff() < 0, True)
    df['is_upper_75'] = False
    df['is_upper_75'] = df['is_upper_75'].where(df['ma_75'].diff() < 0, True)
    # return
    return df


def get_trend(df):
    try:
        df_reverse = df.sort_values('date', ascending=False)
        logger.info("len(df_reverse) {}".format(len(df_reverse)))
        ma_5 = df_reverse['ma_5']
        ma_25 = df_reverse['ma_25']
        ma_75 = df_reverse['ma_75']
        res = dict()
        # 5
        trend_period_5 = 1
        if len(ma_5) > 2 and ma_5.iloc[0] > ma_5.iloc[1]:
            res['is_upper_5'] = True
            for i in range(2, len(df_reverse)):
                if ma_5.iloc[i - 1] > ma_5.iloc[i]:
                    trend_period_5 += 1
                else:
                    break
        elif len(ma_5) > 2 and ma_5.iloc[0] < ma_5.iloc[1]:
            res['is_upper_5'] = False
            for i in range(2, len(df_reverse)):
                if ma_5.iloc[i - 1] < ma_5.iloc[i]:
                    trend_period_5 += 1
                else:
                    break
        # 25
        trend_period_25 = 1
        if len(ma_25) > 2 and ma_25.iloc[0] > ma_25.iloc[1]:
            res['is_upper_25'] = True
            for i in range(2, len(df_reverse)):
                if ma_25.iloc[i-1] > ma_25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        elif len(ma_25) > 2 and ma_25.iloc[0] < ma_25.iloc[1]:
            res['is_upper_25'] = False
            for i in range(2, len(df_reverse)):
                if ma_25.iloc[i-1] < ma_25.iloc[i]:
                    trend_period_25 += 1
                else:
                    break
        # 75
        trend_period_75 = 1
        if len(ma_75) > 2 and ma_75.iloc[0] > ma_75.iloc[1]:
            res['is_upper_75'] = True
            for i in range(2, len(df_reverse)):
                if ma_75.iloc[i-1] > ma_75.iloc[i]:
                    trend_period_75 += 1
                else:
                    break
        elif len(ma_75) > 2 and ma_75.iloc[0] < ma_75.iloc[1]:
            res['is_upper_75'] = False
            for i in range(2, len(df_reverse)):
                if ma_75.iloc[i-1] < ma_75.iloc[i]:
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
        logger.error("ma_5: {}".format(ma_5))
        logger.error("ma_25: {}".format(ma_25))
        logger.error("ma_75: {}".format(ma_75))
        logger.error("df_reverse {}".format(df_reverse))
        res = {
            "is_upper_5": None,
            "period_5": None,
            "is_upper_25": None,
            "period_25": None,
            "is_upper_75": None,
            "period_75": None,
        }
    finally:
        return res


def check(df):
    try:
        trend = get_trend(df)
        df_reverse = df.sort_values('date', ascending=False)
        data = list()
        for i in range(len(df_reverse)-3):
            # たくり線
            if df_reverse.iloc[i]['lower_mustache'] > 2 * df_reverse.iloc[i]['upper_mustache'] \
                    and df_reverse.iloc[i]['lower_mustache'] > 2 * df_reverse.iloc[i]['val_line'] \
                    and not trend['is_upper_25'] and trend['period_25'] > 2:
                msg = "たくり線：底" \
                      + "（ヒゲ：" + str(df_reverse.iloc[i]['lower_mustache']) \
                      + " / 線：" + str(abs(df_reverse.iloc[i]['val_close_open'])) \
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
            if not df_reverse.iloc[i+1]['is_positive'] and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_close']:
                # 陰線→陽線
                if trend['is_upper_25'] and trend['period_25'] > 2:
                    # 上昇傾向→天井
                    msg = "包み陽線：天井（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_天井'].append(df_reverse.iloc[i])
                    data.append({
                        "type": "包線（陰→陽＠上昇）",
                        "is_bottom": False,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
                elif not trend['is_upper_25'] and trend['period_25'] > 2:
                    # 下落傾向→底
                    msg = "包み陽線：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_底'].append(df_reverse.iloc[i])
                    data.append({
                        "type": "包線（陰→陽＠下降）",
                        "is_bottom": True,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
            elif df_reverse.iloc[i+1]['is_positive'] and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_close'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_open'] > df_reverse.iloc[i]['val_close']:
                # 陽線→陰線
                if trend['is_upper_25'] and trend['period_25'] > 2:
                    # 上昇傾向→天井
                    msg = "包み陰線：天井（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_天井'].append(df_reverse.iloc[i])
                    data.append({
                        "type": "包線（陽→陰＠上昇）",
                        "is_bottom": False,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
                elif not trend['is_upper_25'] and trend['period_25'] > 2:
                    # 下落傾向→底
                    msg = "包み陰線：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                    logger.info(msg)
                    # data['包線_底'].append(df_reverse.iloc[i])
                    data.append({
                        "type": "包線（陽→陰＠下降）",
                        "is_bottom": True,
                        "df": df_reverse.iloc[i],
                        "date": df_reverse.iloc[i].date,
                    })
            # 2. はらみ線
            if not df_reverse.iloc[i+1]['is_positive'] \
                    and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_close'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_open'] > df_reverse.iloc[i]['val_close'] \
                    and trend['is_upper_25'] and trend['period_25'] > 2:
                # 陰の陽はらみ
                msg = "陰の陽はらみ：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                # data['はらみ線_底'].append(df_reverse.iloc[i])
                logger.info(msg)
                data.append({
                    "type": "はらみ線（陰→陽＠上昇）",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            elif not df_reverse.iloc[i+1]['is_positive'] \
                    and not df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_close'] \
                    and trend['is_upper_25'] and trend['period_25'] > 2:
                # 陰の陰はらみ
                msg = "陰の陰はらみ：底（" + str(df_reverse.iloc[i+1]['val_line']) + "→" + str(df_reverse.iloc[i]['val_line']) + "）"
                # data['はらみ線_底'].append(df_reverse.iloc[i])
                logger.info(msg)
                data.append({
                    "type": "はらみ線（陰→陰＠上昇）",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            elif df_reverse.iloc[i+1]['is_positive'] \
                    and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+1]['val_open'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+1]['val_close'] > df_reverse.iloc[i]['val_close'] \
                    and not trend['is_upper_25'] and trend['period_25'] > 2:
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
                    and not trend['is_upper_25'] and trend['period_25'] > 2:
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
            if not df_reverse.iloc[i+3]['is_positive'] and not df_reverse.iloc[i+2]['is_positive'] \
                    and not df_reverse.iloc[i+1]['is_positive'] and df_reverse.iloc[i]['is_positive'] \
                    and df_reverse.iloc[i+3]['val_open'] > df_reverse.iloc[i+2]['val_open'] \
                    and df_reverse.iloc[i+3]['val_open'] > df_reverse.iloc[i+1]['val_open'] \
                    and df_reverse.iloc[i+1]['val_close'] < df_reverse.iloc[i]['val_open'] \
                    and df_reverse.iloc[i+3]['val_open'] < df_reverse.iloc[i]['val_close']:
                logger.info("上げ三法：◯")
                # data['上げ三法_底'].append(df_reverse.iloc[i])
                data.append({
                    "type": "上げ三法",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
            # 4. 三空叩き込み
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
            if not df_reverse.iloc[i+2]['is_positive'] \
                    and not df_reverse.iloc[i+1]['is_positive'] \
                    and not df_reverse.iloc[i]['is_positive'] \
                    and -df_reverse.iloc[i+2]['val_close_open'] / df_reverse.iloc[i+2]['val_close'] > 0.05 \
                    and -df_reverse.iloc[i+1]['val_close_open'] / df_reverse.iloc[i+1]['val_close'] > 0.05 \
                    and -df_reverse.iloc[i]['val_close_open'] / df_reverse.iloc[i]['val_close'] > 0.05:
                logger.info("三手大陰線：◯")
                # data['三手大陰線_底'].append(df_reverse.iloc[i])
                data.append({
                    "type": "三手大陰線",
                    "is_bottom": True,
                    "df": df_reverse.iloc[i],
                    "date": df_reverse.iloc[i].date,
                })
    except Exception as e:
        logger.error(e)
    finally:
        return data


def test():
    from web.models import StockValueData
    svds = StockValueData.objects.filter(stock__code=6460).order_by('date')
    df = prepare(svds)
    return df
