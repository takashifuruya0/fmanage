from django.test import TestCase
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SeleniumTest(TestCase):
    def setUp(self) -> None:
        options = Options()
        options.add_argument('--headless')
        if settings.ENVIRONMENT == "metabase":
            options.binary_location = '/usr/bin/google-chrome'
            path = '/usr/bin/chromedriver'
        else:
            path = '/usr/local/bin/chromedriver'
        self.driver = webdriver.Chrome(path, chrome_options=options)

    def tearDown(self) -> None:
        self.driver.close()

    def test_start_selenium(self):
        self.driver.get("https://dot-blog.jp/news/django-readonly-disabled-field/")
        self.assertIsNotNone(self.driver.title)