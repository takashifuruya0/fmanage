from django.test import TestCase
import requests
from django.urls import reverse
from datetime import date
from django.conf import settings
from kakeibo.models import Usages, SharedKakeibos
import logging
logger = logging.getLogger('django')

# Create your tests here.


class GoogleHomeTest(TestCase):
    url = "http://127.0.0.1:8000" + reverse('api:googlehome_shared')
    today = date.today()

    def setUp(self):
        self.data = {
                  "responseId": "6fcaa904-cd91-4e50-a96f-942a9303cb6d",
                  "queryResult": {
                    "queryText": "先月の外食費",
                    "parameters": {
                      "usage_name": "外食費",
                      "date-period": {
                        "startDate": "2018-11-01T12:00:00+09:00",
                        "endDate": "2018-11-30T12:00:00+09:00"
                      },
                      "kakeibo_type": "shared",
                      "query_type": "individual"
                    },
                    "allRequiredParamsPresent": True,
                    "fulfillmentMessages": [
                      {
                        "text": {
                          "text": [
                            ""
                          ]
                        }
                      }
                    ],
                    "intent": {
                      "name": "projects/home-802ab/agent/intents/dbc6c6da-d43f-47c6-abc1-86d73efa6afc",
                      "displayName": "test_shared_individual"
                    },
                    "intentDetectionConfidence": 1,
                    "languageCode": "ja"
                  },
                  "originalDetectIntentRequest": {
                    "payload": {}
                  },
                  "session": "projects/home-802ab/agent/sessions/9e472c5f-16a5-65a9-a97d-a188638d9e0f"
                }

    def test_individual_no_data(self):
        data_in = self.data.copy()
        r = requests.post(self.url, json=data_in)
        logger.debug(self.data['queryResult']['parameters']['usage_name'])
        expected = "2018-11-01から2018-11-30までの外食費の記録はありません。"
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected, r.json()['fulfillmentText'])

    def test_individual_has_data(self):
        data_in = self.data.copy()
        data_in['queryResult']['parameters']['usage_name'] = "食費"
        r = requests.post(self.url, json=data_in)
        expected = "2018-11-01から2018-11-30までの食費の合計は、25958円です。レコード数は、11件です。"
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected, r.json()['fulfillmentText'])

    def test_overview(self):
        data_in = self.data.copy()
        data_in['queryResult']['parameters']['query_type'] = "overview"
        r = requests.post(self.url, json=data_in)
        expected = "2018年11月の支出合計は149913円です。黒字額は、87円、現金精算額は、25801円です。"
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected, r.json()['fulfillmentText'])

    def test_breakdown(self):
        data_in = self.data.copy()
        data_in['queryResult']['parameters']['query_type'] = "breakdown"
        r = requests.post(self.url, json=data_in)
        expected = "2018年11月の支出合計は149913円です。たかしの支出は、115801円、ほうこの支出は、34112円です。"
        expected += "内訳は、家賃104000円、食費25958円、日常消耗品10979円、ガス4216円、電気3980円、その他780円です。"
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected, r.json()['fulfillmentText'])

    def test_post_shared(self):
        data_in = self.data.copy()
        data_in['queryResult']['parameters']['query_type'] = "create"
        data_in['queryResult']['parameters']['date'] = "2017-11-30T12:00:00+09:00"
        data_in['queryResult']['parameters']['fee'] = 0
        data_in['queryResult']['parameters']['usage_name'] = "食費"
        data_in['queryResult']['parameters']['paid_by'] = "敬士"
        r = requests.post(self.url, json=data_in)
        expected = "新しい共通家計簿レコードを追加しました。"
        expected += "2017-11-30の食費、0円、支払い者は敬士です。"
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected, r.json()['fulfillmentText'])


    def test_post_mine(self):
        data_in = self.data.copy()
        data_in['queryResult']['parameters']['query_type'] = "create_mine"
        data_in['queryResult']['parameters']['date'] = "2017-11-30T12:00:00+09:00"
        data_in['queryResult']['parameters']['fee'] = 0
        data_in['queryResult']['parameters']['usage_name'] = "食費"
        data_in['queryResult']['parameters']['way'] = "支出（現金）"
        data_in['queryResult']['parameters']['move_to'] = "None"
        data_in['queryResult']['parameters']['move_from'] = "財布"
        r = requests.post(self.url, json=data_in)
        expected = "新しいマイ家計簿レコードを追加しました。"
        expected += "2017-11-30の支出（現金）、食費、0円です。"
        self.assertEqual(200, r.status_code)
        self.assertEqual(expected, r.json()['fulfillmentText'])
