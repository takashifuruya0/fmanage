from django.core.management.base import BaseCommand
from django.conf import settings
from web.functions import mylib_scraping
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Test scraping'
    CODES = [1357, 1893, "64317081"] # ETF, Stock, Trust
    

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        for CODE in self.CODES:
            self.stdout.write(self.style.SUCCESS(f'--------{CODE}---------'))
            res = mylib_scraping.yf_detail(CODE)
            pprint.pprint(res)