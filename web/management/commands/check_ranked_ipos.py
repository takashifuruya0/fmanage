from django.core.management.base import BaseCommand
from web.models import Stock, Ipo
from web.functions import mylib_selenium
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'check IPOs and detect ranked '

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        try:
            ipod = mylib_selenium.SeleniumIPO()
            res = ipod.get_list()
            for r in res:
                ipos = Ipo.objects.filter(stock__code=r['code']) \
                    .exclude(status__istartswith=3).exclude(status__istartswith=4)
                if ipos.count() == 1:
                    ipo = ipos[0]
                    if ipo.status[0] == "0":
                        ipo.status = '1.評価中'
                    ipo.rank = r.get("rank")
                    ipo.val_predicted = r.get("val_predicted")
                    ipo.url = r.get('url') 
                    ipo.save()
                    self.stdout.write(self.style.SUCCESS(f"{ipo} was updated"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

