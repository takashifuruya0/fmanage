from django.core.management.base import BaseCommand
from django.conf import settings
from web.models import Stock, Ipo
from web.functions import mylib_selenium, mylib_slack
from datetime import date
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'check IPOs and detect ranked '

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        try:
            ipod = mylib_selenium.SeleniumIPO()
            res = ipod.get_list()
            for r in res:
                ipos = Ipo.objects.filter(stock__code=r['code']) \
                    .exclude(status__istartswith=3).exclude(status__istartswith=4)
                if ipos.count() == 1:
                    ipo = ipos[0]
                    if ipo.rank == r.get("rank") and ipo.val_predicted == r.get("val_predicted") and ipo.url == r.get('url'):
                        # 情報が一致→更新しない
                        continue
                    else:
                        # 情報が一致しない→更新＆Slack通知
                        if ipo.status[0] == "0":
                            ipo.status = '1.評価中'
                        ipo.rank = r.get("rank")
                        ipo.val_predicted = r.get("val_predicted")
                        ipo.url = r.get('url')
                        ipo.val_list = r.get("val_list") 
                        ipo.save()
                        self.stdout.write(self.style.SUCCESS(f"{ipo} was updated"))
                        # slack message
                        text = f"""
                            【IPO評価/{date.today()}】
                            ・銘柄：{ipo.stock}
                            ・評価：{ipo.rank}
                            ・予想金額/上場金額：¥{ipo.val_predicted:,}/¥{ipo.val_list:,}
                            詳しくは<https://www.fk-management.com/admin/web/ipo/{ipo.pk}|こちら>
                        """.replace(" ", "")
                        mylib_slack.post_message(url=settings.URL_SLACK_NAMS, text=text)

        except Exception as e:
            self.stderr.write(self.style.ERROR(e))

