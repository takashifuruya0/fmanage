from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from web.models import AssetStatus
from datetime import date


class ViewTest(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user('HogeTaro', 'taro@hoge.com', 'password')
        self.client.force_login(user=self.u)

    def test_main(self):
        url = reverse("web:main")
        self.assertEqual(url, "/nams/")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("web/main.html")

    def test_investment(self):
        url = reverse("web:investment")
        self.assertEqual(url, "/nams/investment/")
        # prepare
        astatus = AssetStatus.objects.create(
            date=date.today(), investment=100,
            sum_stock=0, sum_other=0, sum_trust=0,
            buying_power=100, nisa_power=1000000,
            user=self.u,
        )
        # is_investment=TrueでPOST
        response = self.client.post(
            url, data={
                "value": 100,
                "is_investment": True,
            }
        )
        # トップページへリダイレクト
        self.assertRedirects(response, reverse('web:main'))
        # is_investment=Trueなのでbuying_power, investement両方が増加
        self.assertEqual(AssetStatus.objects.get(pk=astatus.pk).buying_power, 200)
        self.assertEqual(AssetStatus.objects.get(pk=astatus.pk).investment, 200)
        # is_investment=FalseでPOST
        response = self.client.post(
            url, data={
                "value": 100,
                "is_investment": False,
            }
        )
        # トップページへリダイレクト
        self.assertRedirects(response, reverse('web:main'))
        # is_investment=Falseなのでbuying_powerのみ両方が増加
        self.assertEqual(AssetStatus.objects.get(pk=astatus.pk).buying_power, 300)
        self.assertEqual(AssetStatus.objects.get(pk=astatus.pk).investment, 200)
