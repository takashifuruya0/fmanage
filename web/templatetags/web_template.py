from django import template
register = template.Library()


@register.filter
def yen(val, digit=0):
    if not val:
        return "-"
    elif val >= 0 and digit == 0:
        return "¥{:,}".format(round(val))
    elif val >= 0 and digit > 0:
        return "¥{:,}".format(round(val, digit))
    elif val < 0 and digit == 0:
        return "<font color='red'>-¥{:,}</font>".format(round(-val))
    else:
        return "<font color='red'>-¥{:,}</font>".format(round(-val, digit))