from django.core.management.base import BaseCommand
from kakeibo.functions import calc_val
from kakeibo.models import Resources
import logging
logger = logging.getLogger('django')


class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Updating current_val'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        msg = "This command is not activated now"
        self.stdout.write(self.style.SUCCESS(msg)
        logger.info(msg)
        # name = [i.name for i in Resources.objects.all()]
        # for i in name:
        #     r = calc_val.resource_current_val(i, 0)
        #     if r['status'] is True:
        #         self.stdout.write(self.style.SUCCESS(r['msg']))
        #         logger.info(r['msg'])
        #     else:
        #         self.stderr.write(r['msg'])
        #         logger.error(r['msg'])
