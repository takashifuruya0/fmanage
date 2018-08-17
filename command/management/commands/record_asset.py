from django.core.management.base import BaseCommand

from asset.functions import mylib_asset as ac


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Test commands'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッドupdate_credit.py
    def handle(self, *args, **options):
        # self.stdout.write(self.style.SUCCESS('Article count = "%s"' % kakeibos_count))
        ac.record_status()
        self.stdout.write(self.style.SUCCESS('test'))
