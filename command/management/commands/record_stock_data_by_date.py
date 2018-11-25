from django.core.management.base import BaseCommand

from asset.models import StockDataByDate, Stocks
from asset.functions import get_info
import logging
logger = logging.getLogger("django")



# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'kabuoji3.comからレコードを取得し、StockDataByDateに保存'

    # コマンドが実行された際に呼ばれるメソッドupdate_credit.py
    def handle(self, *args, **options):
        stocks = Stocks.objects.all()
        for stock in stocks:
            # kabuoji3.comから取得
            data = get_info.kabuoji3(stock.code)
            if data['status']:
                # 取得成功時
                for d in data['data']:
                    # (date, stock)の組み合わせでデータがなければ追加
                    if StockDataByDate.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                        sdbd = StockDataByDate()
                        sdbd.stock = stock
                        sdbd.date = d[0]
                        sdbd.val_start = d[1]
                        sdbd.val_high = d[2]
                        sdbd.val_low = d[3]
                        sdbd.val_end = d[4]
                        sdbd.turnover = d[5]
                        sdbd.save()
                self.stdout.write(self.style.SUCCESS('StockDataByDate of "%s" are updated' % stock.code))
            else:
                # 取得失敗時
                logger.error(data['msg'])
                self.stderr.write(data['msg'])

        self.stdout.write(self.style.SUCCESS('StockDataByDate are updated'))
