from django.core.management.base import BaseCommand
from asset.functions import mylib_asset
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Updating/Creating AssetStatus for today'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):

        r = mylib_asset.record_status()
        if r['status']:
            self.stdout.write(self.style.SUCCESS(r['memo']))
            logger.info(r['memo'])
        else:
            self.stderr.write(r['memo'])
            logger.error(r['memo'])
