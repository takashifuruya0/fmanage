from django.core.management.base import BaseCommand
from lancers.models import Opportunity
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Copy Regular Opportunities'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # def add_arguments(self, parser):
    #     parser.add_argument('todo')

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        opps = Opportunity.objects.filter(is_regular=True, status="選定/作業中", is_copied_to=False)
        if opps.count() == 0:
            msg = "No opportunities were copied"
            self.stdout.write(self.style.SUCCESS(msg))
            return
        u = get_user_model().objects.first()
        for opp in opps:
            opp_copied_from = Opportunity.objects.get(pk=opp.pk)
            # 複製処理
            opp.pk = None
            opp.created_at = None
            opp.sync_id = None
            opp.date_open = opp.date_open + relativedelta(months=1)
            opp.date_close = opp.date_close + relativedelta(months=1)
            opp.date_proposed_delivery = opp.date_proposed_delivery + relativedelta(months=1)
            opp.status = "相談中"
            if not opp.original_opportunity:
                opp.original_opportunity = opp_copied_from
            opp.save_from_shell(user=u)
            # 成功後の処理
            opp_copied_from.is_copied_to = True
            opp_copied_from.save_from_shell(user=u)
            # msg
            msg = "Created successfully: {}".format(opp)
            self.stdout.write(self.style.SUCCESS(msg))
