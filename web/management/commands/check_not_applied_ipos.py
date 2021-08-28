from django.core.management.base import BaseCommand
from django.conf import settings
from web.models import Stock, Ipo
from web.functions import mylib_scraping, mylib_slack
from datetime import datetime, timezone, date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'check and detect not-applied IPOs '

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        try:
            now = datetime.now(timezone.utc)
            ipos = Ipo.objects.filter(datetime_open__lte=now, datetime_close__gte=now, is_applied=False)
            if ipos.count() == 0:
                # 申込対象なし
                self.stdout.write("Not-applied IPO was not found")
            for ipo in ipos:
                # 申し込み対象あり
                text = f"""
                    【IPO申込開始!/{date.today()}】
                    ・銘柄：{ipo.stock}
                    ・評価：{ipo.rank}
                    ・申込期間：{ipo.datetime_open.date()}〜{ipo.datetime_close.date()}
                    ・抽選日：{ipo.datetime_select.date()}
                    詳しくは<https://www.fk-management.com/admin/web/ipo/{ipo.pk}|こちら>
                """.replace(" ", "")
                mylib_slack.post_message(url=settings.URL_SLACK_LOG, text=text)
                self.stdout.write(self.style.SUCCESS(f"Post slack notification on booking for {ipo}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

