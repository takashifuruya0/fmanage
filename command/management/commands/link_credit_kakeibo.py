from django.core.management.base import BaseCommand
from kakeibo.models import Credits, Kakeibos, Usages
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
        credits = Credits.objects.all()
        kcs = Kakeibos.objects.filter(way="支出（クレジット）")
        other = Usages.objects.get(name="その他")
        counter = [0, 0, 0, 0]
        msgs = []
        for c in credits:
            try:
                if c.kakeibo:
                    continue
                check = kcs.filter(fee=c.fee, date__year=c.date.year, date__month=c.date.month)
                num = check.count()
                if num == 1 and check[0].credits_set.count() == 0:
                    c.kakeibo = check[0]
                    c.save()
                    counter[1] += 1
                elif num == 0:
                    k = Kakeibos()
                    k.date = c.date
                    k.fee = c.fee
                    k.way = "支出（クレジット）"
                    if c.credit_item:
                        k.usage = c.credit_item.usage
                        k.memo = c.credit_item.name
                    else:
                        k.usage = other
                    k.save()
                    c.kakeibo = k
                    c.save()
                    counter[0] += 1
                else:
                    for ck in check:
                        if ck.usage == c.credit_item.usage and ck.credits_set.count() == 0:
                            c.kakeibo = ck
                            c.save()
                            counter[2] += 1
                            break
                        else:
                            msgs.append("{} is not {}".format(c.credit_item.usage, ck.usage))
                            pass

            except Exception as e:
                self.stdout.write(e)
        smsg = "0:{}, 1:{}, matched:{}".format(counter[0], counter[1], counter[2])
        if smsg != "":
            self.stdout.write(self.style.SUCCESS(smsg))
            self.stdout.write("{}".format(msgs))
            logger.info(smsg)
