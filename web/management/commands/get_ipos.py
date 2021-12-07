from django.conf import settings
from django.core.management.base import BaseCommand
from web.functions.mylib_selenium import SeleniumSBI
from web.functions import mylib_slack
from web.models import Stock, Ipo
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'update IPOs'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        
        sbi = SeleniumSBI()
        res = sbi.get_ipos()
        for d in res['data']:
            try:
                self.stdout.write(f"============={d['name']}=================")
                if Stock.objects.filter(code=d['code']).exists():
                    s = Stock.objects.get(code=d['code'])
                    self.stdout.write(self.style.SUCCESS("Found Stock {}".format(s)))
                else:
                    s = Stock.objects.create(
                        code=d['code'], name=d['name'], market=d['market'], unit=d['unit'],
                        is_listed=False, is_trust=False
                    )
                    self.stdout.write(self.style.SUCCESS("Stock {} was created successfully".format(s)))
                if Ipo.objects.filter(stock=s).exists():
                    ipo = Ipo.objects.get(stock=s)
                    # update対象項目のみ
                    ipo.val_list = d["val_list"]
                    ipo.num_applied = d["num_applied"]
                    ipo.point = d["point"]
                    ipo.result_select = d['result_select']
                    ipo.result_buy = d["result_buy"]
                    if d["num_applied"]:
                        ipo.is_applied = d["is_applied"]
                        if d['result_select'] == "落選" and not "落選" in ipo.status:
                            # 落選だった場合
                            ipo.status = "3.落選（上場前）"
                            # slack message
                            text = f"""
                                【IPO落選。。。/{date.today()}】
                                ・銘柄：{ipo.stock}
                                詳しくは<https://www.fk-management.com/admin/web/ipo/{ipo.pk}|こちら>
                            """.replace(" ", "")
                            mylib_slack.post_message(url=settings.URL_SLACK_NAMS, text=text)
                        elif "当選" in d['result_select'] and not "当選" in ipo.status:
                            # 当選だった場合
                            ipo.status = "3.当選（上場前）"
                            # 補欠当選／100株
                            ipo.num_select = int(d['result_select'].replace("株", "").replace("口", "").split("／")[1])
                            # slack message
                            data = mylib_slack.param_ipo_selected(ipo)
                            mylib_slack.post_rich_message(data)
                        else:
                            ipo.status = "2.申込済"
                    else:
                        ipo.status = "1.評価中"
                    # save
                    ipo.save()
                    self.stdout.write(self.style.SUCCESS("IPO {} was updated successfully".format(ipo)))
                else:
                    ipo = Ipo.objects.create(
                        stock=s,
                        datetime_open=d['datetime_open'],
                        datetime_close=d['datetime_close'],
                        # status=d["status"],
                        val_list=d["val_list"],
                        is_applied=d["is_applied"],
                        num_applied=d["num_applied"],
                        point=d["point"],
                        date_list=d["date_list"],
                        datetime_select=d["datetime_select"],
                        result_select=d['result_select'],
                        datetime_purchase_close=d["datetime_purchase_close"],
                        datetime_purchase_open=d["datetime_purchase_open"],
                        result_buy=d["result_buy"],
                    )
                    self.stdout.write(self.style.SUCCESS("IPO {} was created successfully".format(ipo)))
                    # slack message
                    text = f"""
                        【IPO登録/{date.today()}】
                        ・銘柄：{ipo.stock}
                        ・申込期間：{ipo.datetime_open.date()}〜{ipo.datetime_close.date()}
                        ・抽選日：{ipo.datetime_select.date()}
                        詳しくは<https://www.fk-management.com/admin/web/ipo/{ipo.pk}|こちら>
                    """.replace(" ", "")
                    mylib_slack.post_message(url=settings.URL_SLACK_NAMS, text=text)
            except Exception as e:
                self.stderr.write(self.style.ERROR(e))
        sbi.close()
