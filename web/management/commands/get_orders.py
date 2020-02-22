from django.core.management.base import BaseCommand
from web.models import Stock, StockValueData
from web.functions import data_migration
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Sync Order from asset to web'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        data_migration.stock()
        result = data_migration.order()
        msg = "Result of get_orders: {}".format(result)
        self.stdout.write(self.style.SUCCESS(msg))
