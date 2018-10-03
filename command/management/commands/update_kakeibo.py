from django.core.management.base import BaseCommand
from kakeibo.functions import update_records
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Updating kakeibo-record'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        # smsg, emsg = update_records.save_kakeibo_to_sql()
        smsg, emsg = update_records.update_kakeibo_to_sql()
        if smsg != "":
            self.stdout.write(self.style.SUCCESS(smsg))
            logger.info(smsg)
        else:
            self.stderr.write(emsg)
            logger.error(emsg)
