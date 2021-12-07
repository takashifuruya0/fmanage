from django.conf import settings
from django.core.management.base import BaseCommand
from web.functions.mylib_selenium import SeleniumSBI
from web.functions import mylib_selenium
from web.models import Stock, Ipo
from datetime import datetime
import pytz
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'apply IPOs'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        now_jst = datetime.now(pytz.timezone('Asia/Tokyo'))
        ipos = Ipo.objects.filter(is_applied=False, datetime_open__lte=now_jst, datetime_close__gte=now_jst)
        is_booting = False
        num = 100
        for i in range(3):
            try:
                sbi = mylib_selenium.SeleniumSBI()
                is_booting = True
                break
            except Exception as e:
                self.stdout.write(self.style.WARNING(e))
        if not is_booting:
            self.stdout.write(self.style.ERROR('Failed to boot up selenium'))
            return
        for ipo in ipos:
            self.stdout.write(f"----------- {ipo.stock} ----------")
            try:
                res = sbi.apply_ipo(ipo.stock.code, num)
                if res['status']:
                    ipo.status = "2.申込済"
                    ipo.is_applied = True
                    ipo.num_applied = num
                    ipo.date_applied = now_jst.today()
                    ipo.save()
                    self.stdout.write(self.style.SUCCESS(f"Successfully applied IPO for {ipo.stock}"))
                else:
                    self.stdout.write(self.style.WARNING(res['msg']))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        sbi.close()