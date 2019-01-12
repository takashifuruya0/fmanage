from django.core.management.base import BaseCommand
from kakeibo.functions import auto_import
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger('django')
from kakeibo.models import CreditItems, Credits


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
            data = auto_import.goldpoint(target.year, target.month)['data']
            logger.info(data)
            for d in data:
                # CreditItemがあるかどうかチェック
                # 連続半角スペースを単一半角スペースに変換
                name = d['credit_item'].replace("  ", " ")
                citems = CreditItems.objects.filter(name=name)
                if len(citems) == 1:
                    citem = citems[0]
                elif len(citems) == 0:
                    citem = CreditItems.objects.create(date=today, name=name)
                    logger.info("New citem was created: {0}".form(citem))
                # Creditがあるかチェック
                credit_records = Credits.objects.filter(
                    date=d['date'], debit_date=d['debit_date'], fee=d['fee'], credit_item=citem
                )
                if len(credit_records) == 0:
                    Credits.objects.create(
                        date=d['date'], debit_date=d['debit_date'],
                        fee=d['fee'], credit_item=citem
                    )
                    logger.info("Created a new record for No.{0}".format(d['no']))
                else:
                    logger.info("The record for No.{0} exists".format(d['no']))
        # msg
        msg = "Done"
        self.stdout.write(self.style.SUCCESS(msg))
        logger.info(msg)
