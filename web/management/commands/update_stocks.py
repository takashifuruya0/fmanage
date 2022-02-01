from django.core.management.base import BaseCommand
from web.models import Stock, StockAnalysisData
from web.functions import mylib_asset
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Update stocks'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        for s in stocks:
            s.save()
            msg = "{} is updated".format(s)
            self.stdout.write(self.style.SUCCESS(msg))
