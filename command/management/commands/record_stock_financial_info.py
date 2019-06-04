from django.core.management.base import BaseCommand
from asset.functions import mylib_asset as ac
from asset.models import Stocks


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Test commands'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッドupdate_credit.py
    def handle(self, *args, **options):
        # self.stdout.write(self.style.SUCCESS('Article count = "%s"' % kakeibos_count))
        counter = 0
        counter_skip = 0
        for s in Stocks.objects.all():
            try:
                check = ac.register_stock_financial_info(s.code)
                if check:
                    counter += 1
                    self.stdout.write(self.style.SUCCESS("{}:{} was saved".format(s.code, s.name)))
                else:
                    counter_skip += 1
            except Exception as e:
                pass
        self.stdout.write(self.style.SUCCESS('{}件保存、{}件スキップしました'.format(counter, counter_skip)))
