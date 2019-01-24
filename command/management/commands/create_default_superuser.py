from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Init Colors'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # 今回はblog_idという名前で取得する。（引数は最低でも1個, int型）

    # コマンドが実行された際に呼ばれるメソッドupdate_credit.py
    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "", "Admin1234")
            self.stdout.write(self.style.SUCCESS('The default admin user was created.'))
        else:
            self.stdout.write(self.style.SUCCESS('The default admin user exists.'))
