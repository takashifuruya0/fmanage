from django.core.management.base import BaseCommand
from kakeibo.functions import auto_import
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger('django')


class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Updating credit-records of goldpoint-card by selenium'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        today = date.today()
        for i in range(6):
            target = today - relativedelta(months=i)
            self.stdout.write(str(target))
            records = auto_import.goldpoint(target.year, target.month)['data']
            logger.info(records)
        msg = "Done"
        self.stdout.write(self.style.SUCCESS(msg))
        logger.info(msg)
