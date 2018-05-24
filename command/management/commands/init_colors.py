from django.core.management.base import BaseCommand

from kakeibo.models import Colors


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Init Colors'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッドupdate_credit.py
    def handle(self, *args, **options):
        color_list = [
            "dimgrey", "darkgrey",
        ]
        current_list = [i.name for i in Colors.objects.all()]
        tmp = 0
        for color in color_list:
            if not color in current_list: 
                Colors(name=color).save()
                tmp += 1
        self.stdout.write(self.style.SUCCESS('"%s" colors were added' % tmp))
