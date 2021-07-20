from django.core.management.base import BaseCommand
from web.functions.mylib_selenium import SeleniumSBI
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
        try:
            sbi = SeleniumSBI()
            res = sbi.get_ipos()
            for d in res['data']:
                if Stock.objects.filter(code=d['code']).exists():
                    s = Stock.objects.get(code=d['code'])
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
                        if d['result_select'] == "落選":
                            ipo.status = "3.落選（上場前）"
                        elif d['result_select'] == "当選":
                            ipo.status = "3.当選（上場前）"
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
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))
        finally:
            sbi.close()
