import logging
logger = logging.getLogger("django")
from datetime import date, datetime
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders, StockDataByDate
# pandas
from django_pandas.io import read_frame


def set_analysis_to_df(df):
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
    # return
    return df


def get_cross(df):
    cross = {
        "golden": list(),
        "dead": list(),
        "date": list(),
        "recent_golden": None,
        "recent_dead": None,
    }
    for i in range(1, len(df)):
        if df.iloc[i - 1]['ma_diff'] < 0 and df.iloc[i]['ma_diff'] > 0:
            print("{}:GGOLDEN CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(df.iloc[i]['ma25'])
            cross['dead'].append(None)
            cross['recent_golden'] = df.iloc[i]["date"]
        elif df.iloc[i - 1]['ma_diff'] > 0 and df.iloc[i]['ma_diff'] < 0:
            print("{}:DEAD CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(None)
            cross['dead'].append(df.iloc[i]['ma25'])
            cross['recent_dead'] = df.iloc[i]["date"]
        else:
            cross['golden'].append(None)
            cross['dead'].append(None)
        cross['date'].append(df.iloc[i]["date"])
    return cross
