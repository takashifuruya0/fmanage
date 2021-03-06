from django.core.management.base import BaseCommand
from web.functions import mylib_asset
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Record AssetStatus by coping the latest data'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        d = mylib_asset.record_asset_status()
        if d['status']:
            msg = "Result of record_asset_status: {}".format(d['asset_status'])
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write("Failed to execute 'record_asset_status_alt'")
