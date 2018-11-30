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
            print("{}:GOLDEN CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(df.iloc[i]['ma_25'])
            cross['dead'].append(None)
            cross['recent_golden'] = df.iloc[i]["date"]
        elif df.iloc[i - 1]['ma_diff'] > 0 and df.iloc[i]['ma_diff'] < 0:
            print("{}:DEAD CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(None)
            cross['dead'].append(df.iloc[i]['ma_25'])
            cross['recent_dead'] = df.iloc[i]["date"]
        else:
            cross['golden'].append(None)
            cross['dead'].append(None)
    return cross


def bollinger(df, window=25):
    df1 = df.copy()
    df1["ma"] = df1.close.rolling(window=window).mean()
    df1["sigma"] =  df1.close.rolling(window=window).std()
    df1["ma+2sigma"] = df1.ma + 2*df1.sigma
    df1["ma-2sigma"] = df1.ma - 2*df1.sigma
    df1["diffplus"] = df1.close - df1["ma+2sigma"]
    df1["diffminus"] = df1["ma-2sigma"] - df1.close
    s_up = df1[df1["diffplus"]>0]["close"]
    s_down = df1[df1["diffminus"]>0]["close"]

    return