from django.shortcuts import render

import logging
logger = logging.getLogger("django")
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime


# 概要
def dashboard(request):
    # return
    output = {
        "today": date.today(),
    }
    return render(request, 'asset/dashboard.html', output)


