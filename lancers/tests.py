from django.test import TestCase
from lancers.models import *
from django.contrib.auth import get_user_model
# Create your tests here.


class ModelTest(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        # Client
        self.cl = Client(name="共通クライアント", client_id="0", is_nonlancers=False, client_type="Lancers")
        self.cl.save_from_shell(self.user)
        # Category
        self.cg = Category(name="共通カテゴリ")
        self.cg.save_from_shell(self.user)

    def test_client_create(self):
        num_before = Client.objects.count()
        # create
        name = "テストクライアント"
        client_id = "1"
        client_type = "MENTA"
        is_nonlancers = True
        cl = Client(name=name, client_id=client_id, is_nonlancers=is_nonlancers, client_type=client_type)
        cl.save_from_shell(self.user)
        self.assertEqual(Client.objects.count(), num_before+1)
        self.assertEqual(cl.name, name)
        self.assertEqual(cl.client_id, client_id)

    def test_opportunity_create(self):
        num_before = Opportunity.objects.count()
        # Opportunity
        op = Opportunity(client=self.cl, name="テスト商談", category=self.cg, status="相談中", type="直接受注", val=10000)
        op.save_from_shell(self.user)
        self.assertEqual(Opportunity.objects.count(), num_before+1)
