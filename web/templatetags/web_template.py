from django import template
register = template.Library()


@register.filter
def yen(val, digit=0):
    if val >= 0:
        return "¥{:,}".format(round(val, digit))
    else:
        return "<font color='red'>-¥{:,}</font>".format(round(val, digit))