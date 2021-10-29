from django.core.management.base import BaseCommand
from kakeibo.models import CronKakeibo, Kakeibos, CronShared, SharedKakeibos
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Test commands'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッドupdate_credit.py
    def handle(self, *args, **options):
        # self.stdout.write(self.style.SUCCESS('Article count = "%s"' % kakeibos_count))
        # 家計簿
        try:
            cks = CronKakeibo.objects.all()
            for ck in cks:
                data = {
                    "fee": ck.fee,
                    "move_from": ck.move_from,
                    "move_to": ck.move_to,
                    "way": ck.way,
                    "usage": ck.usage,
                    "date": date.today(),
                    "memo": "Created from CronKakeibo",
                    "currency": ck.currency,
                }
                Kakeibos.objects.create(**data)
            self.stdout.write(self.style.SUCCESS('completed CronKakeibo.'))
        except Exception as e:
            self.stderr.write('failed CronKakeibo.')
            self.stderr.write("".format(e))
            logger.error(e)
        # 共通家計簿
        try:
            css = CronShared.objects.all()
            for cs in css:
                data = {
                    "fee": cs.fee,
                    "move_from": cs.move_from,
                    "way": cs.way,
                    "usage": cs.usage,
                    "paid_by": cs.paid_by,
                    "date": date.today(),
                    "memo": "Created from CronShared"
                }
                SharedKakeibos.objects.create(**data)
            self.stdout.write(self.style.SUCCESS('completed CronShared.'))
        except Exception as e:
            self.stderr.write('failed CronShared.')
            self.stderr.write("".format(e))
            logger.error(e)
