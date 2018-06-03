# coding:utf-8
# 円通貨表示にする．数字以外は-とする


def convert_yen(v):
    v = int(v)
    try:
        if v >= 0:
            new_val = '¥{:,}'.format(v)
        elif v < 0:
            new_val = '-¥{:,}'.format(-v)
    except Exception as e:
            new_val = "-"
    return new_val
