from django.core.management.base import BaseCommand
from web.models import Stock, Ipo
from web.functions import mylib_scraping
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'check IPOs and detect listed '

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        try:
            today = date.today()
            ipos = Ipo.objects.filter(date_list=today)
            if ipos.count() == 0:
                # 上場したデータなし
                self.stdout.write("Listed IPO was not found")
            for ipo in ipos:
                # is_listed
                ipo.stock.is_listed = True
                ipo.stock.save()
                msg = "{} have been listed and the data was updated".format(ipo.stock)
                self.stdout.write(self.style.SUCCESS(msg))
                # status
                if ipo.status == "3.当選（上場前）":
                    ipo.status = "4.当選（上場後）"
                else:
                    ipo.status = "4.落選（上場後）"
                # 初値
                d = mylib_scraping.yf_detail(ipo.stock.code)
                if d['status']:
                    ipo.val_initial = d['data']['val_open']
                    msg = "val_initial of {} was updated".format(ipo.stock)
                    msg_write = self.style.SUCCESS(msg)
                else:
                    msg_write = "Cannot set val_initial to {} because of the fail to scrape data".format(ipo.stock)
                ipo.save()
                self.stdout.write(msg_write)
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

