from django.core.management.base import BaseCommand
from web.models import Stock
from web.functions import mylib_slack
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Record StockValueData by scraping kabuoji3'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        res = mylib_slack.post_open_entries()
        self.stdout.write(res)
