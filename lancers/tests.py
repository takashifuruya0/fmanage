from django.test import TestCase
from lancers.models import *
from django.contrib.auth import get_user_model
# Create your tests here.


class ModelTest(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user('HogeTaro', 'taro@hoge.com', 'password')

    def test_client_create(self):
        name = "テストクライアント"
        client_id = "0"
        client_type = "MENTA"
        is_nonlancers = True
        cl = Client(name=name, client_id=client_id, is_nonlancers=is_nonlancers, client_type=client_type)
        cl.save_from_shell(self.user)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(cl.name, name)
        self.assertEqual(cl.client_id, client_id)
