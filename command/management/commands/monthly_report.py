from django.core.management.base import BaseCommand
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'monthly report'

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        # 先月のyear, monthを取得
        # 先月bars_shared_eom を画像として保存
        # mail