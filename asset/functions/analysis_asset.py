import logging
logger = logging.getLogger("django")
from datetime import date, datetime
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders, StockDataByDate
# pandas
from django_pandas.io import read_frame


def analyse_stock_data(df):
    # 終値前日比, 出来高前日比
    df['val_end_diff'] = -(df['val_end'].shift() - df['val_end'])
    df['val_end_diff_percent'] = round(-(df['val_end'].shift() - df['val_end']) / df['val_end'].shift() * 100, 1)
    df['turnover_diff'] = -(df['turnover'].shift() - df['turnover'])
    df['turnover_diff_percent'] = round(-(df['turnover'].shift() - df['turnover']) / df['turnover'].shift() * 100, 1)
    # 終値-始値
    df['val_end-start'] = df['val_end'] - df['val_start']
    # 陽線/陰線
    df['is_positive'] = False
    df['is_positive'] = df['is_positive'].where(df['val_end-start'] < 0, True)
    # 下ひげ
    df['lower_mustache'] = (df['val_start'] - df['val_low']).where(df['is_positive'], df['val_end'] - df['val_low'])
    # 上ひげ
    df['upper_mustache'] = (df['val_high'] - df['val_end']).where(df['is_positive'], df['val_high'] - df['val_start'])
    # 移動平均
    df['ma_25'] = df.val_end.rolling(window=25, min_periods=1).mean()
    df['ma_75'] = df.val_end.rolling(window=75, min_periods=1).mean()
    df['ma_diff'] = df.ma_25 - df.ma_75
    # ボリンジャーバンド（25日）
    df["sigma_25"] = df.val_end.rolling(window=25).std()
    df["ma_25p2sigma"] = df.ma_25 + 2 * df.sigma_25
    df["ma_25m2sigma"] = df.ma_25 - 2 * df.sigma_25
    # df["diffplus"] = df.val_end - df["ma_25+2sigma"]
    # df["diffminus"] = df["ma_25-2sigma"] - df.val_end
    # s_up = df[df["diffplus"] > 0]["close"]
    # s_down = df[df["diffminus"] > 0]["close"]
    # return
    return df


def get_cross(df_orig):
    # nanを含む列は除外
    df = df_orig.dropna()
    cross = {
        "golden": [None, ],
        "dead": [None, ],
        "recent_golden": None,
        "recent_dead": None,
    }
    for i in range(1, len(df)):
        if df.iloc[i - 1]['ma_diff'] < 0 and df.iloc[i]['ma_diff'] > 0:
            logger.log("{}:GOLDEN CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(df.iloc[i]['ma_25'])
            cross['dead'].append(None)
            cross['recent_golden'] = df.iloc[i]["date"]
        elif df.iloc[i - 1]['ma_diff'] > 0 and df.iloc[i]['ma_diff'] < 0:
            logger.log("{}:DEAD CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(None)
            cross['dead'].append(df.iloc[i]['ma_25'])
            cross['recent_dead'] = df.iloc[i]["date"]
        else:
            cross['golden'].append(None)
            cross['dead'].append(None)
    return cross


def check_mark(df):
    # mark
    mark = list()

    # 0. たくり線・勢力線// 前日にカラカサか下影陰線→◯。3日前~2日前で陰線だったら◎
    if df.iloc[0]['lower_mustache'] > 2*df.iloc[0]['upper_mustache'] \
            and df.iloc[1]['val_end_diff'] < 0 \
            and df.iloc[2]['val_end_diff'] < 0:
        if not df.iloc[1]['is_positive'] and not df.iloc[2]['is_positive']:
            mark.append("◎")
        else:
            mark.append("◯")
    else:
        mark.append("")

    # 1. 包線
    if not df.iloc[1]['is_positive'] and df.iloc[0]['is_positive']:
        # 陰線→陽線
        logger.log("陰線→陽線"+str(df[['val_start', 'val_end']][0:2]))
        if df.iloc[1]['val_end'] < df.iloc[0]['val_start'] and df.iloc[1]['val_start'] > df.iloc[0]['val_end']:
            # 長→短
            mark.append("包み陽線：天井")
        elif df.iloc[1]['val_end'] > df.iloc[0]['val_start'] and df.iloc[1]['val_start'] < df.iloc[0]['val_end']:
            # 短→長
            mark.append("包み陽線：底")
        else:
            mark.append("")
    elif df.iloc[1]['is_positive'] and not df.iloc[0]['is_positive']:
        # 陽線→陰線
        logger.log("陽線→陰線"+str(df[['val_start', 'val_end']][0:2]))
        if df.iloc[1]['val_end'] < df.iloc[0]['val_start'] and df.iloc[1]['val_start'] > df.iloc[0]['val_end']:
            # 短→長
            mark.append("包み陰線：底")
        elif df.iloc[1]['val_end'] > df.iloc[0]['val_start'] and df.iloc[1]['val_start'] < df.iloc[0]['val_end']:
            # 長→短
            mark.append("包み陰線：天井")
        else:
            mark.append("")
    else:
        mark.append("")

    # 2. はらみ線
    if not df.iloc[1]['is_positive'] \
            and df.iloc[0]['is_positive'] \
            and df.iloc[1]['val_end'] < df.iloc[0]['val_start'] \
            and df.iloc[1]['val_start'] > df.iloc[0]['val_end']:
        # 陰の陽はらみ
        mark.append("陰の陽はらみ：底")
        logger.log("陰の陽はらみ：底")
    elif not df.iloc[1]['is_positive'] \
            and not df.iloc[0]['is_positive'] \
            and df.iloc[1]['val_start'] < df.iloc[0]['val_start'] \
            and df.iloc[1]['val_end'] > df.iloc[0]['val_end']:
        # 陰の陰はらみ
        mark.append("陰の陰はらみ：底")
        logger.log("陰の陰はらみ：底")
    elif df.iloc[1]['is_positive'] \
            and df.iloc[0]['is_positive'] \
            and df.iloc[1]['val_start'] < df.iloc[0]['val_start'] \
            and df.iloc[1]['val_end'] > df.iloc[0]['val_end']:
        # 陽の陽はらみ
        mark.append("陽の陽はらみ：天井")
        logger.log("陽の陽はらみ：天井")
    elif not df.iloc[1]['is_positive'] \
            and not df.iloc[0]['is_positive'] \
            and df.iloc[1]['val_start'] < df.iloc[0]['val_end'] \
            and df.iloc[1]['val_end'] > df.iloc[0]['val_start']:
        # 陽の陽はらみ
        mark.append("陽の陽はらみ：天井")
        logger.log("陽の陽はらみ：天井")
    else:
        mark.append("")

    # 3. 上げ三法: 1本目の安値を割り込まない, 4本目が1本目の終値を超える
    if not df.iloc[3]['is_positive'] and not df.iloc[2]['is_positive'] \
            and not df.iloc[1]['is_positive'] and df.iloc[0]['is_positive'] \
            and df.iloc[3]['val_start'] > df.iloc[2]['val_start'] \
            and df.iloc[3]['val_start'] > df.iloc[1]['val_start'] \
            and df.iloc[1]['val_end'] > df.iloc[0]['val_start'] \
            and df.iloc[3]['val_start'] > df.iloc[0]['val_end']:
        mark.append("◯")
    else:
        mark.append("")

    # 4. 三空叩き込み
    if not df.iloc[3]['is_positive'] and not df.iloc[2]['is_positive'] \
            and not df.iloc[1]['is_positive'] and not df.iloc[0]['is_positive'] \
            and df.iloc[3]['val_start'] < df.iloc[2]['val_end'] \
            and df.iloc[2]['val_start'] < df.iloc[1]['val_end'] \
            and df.iloc[1]['val_start'] < df.iloc[0]['val_end']:
        mark.append("◯")
        logger.log("三空叩き込み")
    else:
        mark.append("")

    # 5. 三手大陰線
    if not df.iloc[2]['is_positive'] and not df.iloc[1]['is_positive'] and not df.iloc[0]['is_positive'] \
            and -df.iloc[2]['val_end-start'] / df.iloc[2]['val_end'] > 0.05 \
            and -df.iloc[1]['val_end-start'] / df.iloc[1]['val_end'] > 0.05 \
            and -df.iloc[0]['val_end-start'] / df.iloc[0]['val_end'] > 0.05:
        mark.append("◯")
        logger.log("三手大陰線")
    else:
        mark.append("")

    return mark
