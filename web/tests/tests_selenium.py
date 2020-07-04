from django.test import TestCase
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# class SeleniumTest(TestCase):
#     def setUp(self) -> None:
#         if settings.ENVIRONMENT == 'metabase':
#             # linux
#             options = Options()
#             options.binary_location = '/usr/bin/google-chrome'
#             options.add_argument('--headless')
#             options.add_argument('--window-size=1280,1024')
#             self.driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
#         elif settings.ENVIRONMENT == 'develop':
#             # mac
#             self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
#
#     def tearDown(self) -> None:
#         self.driver.close()
#
#     def test_start_selenium(self):
#         self.driver.get("https://dot-blog.jp/news/django-readonly-disabled-field/")
#         self.assertIsNotNone(self.driver.title)