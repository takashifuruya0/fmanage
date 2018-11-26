# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
from . import views


app_name = 'asset'
urlpatterns = [
    # updates
    url(r'^$', views.asset_dashboard, name='dashboard'),
    url(r'^stocks/create$', views.StocksCreateView.as_view(), name='stocks_create'),
    url(r'^hstocks/create$', views.HoldingStocksCreateView.as_view(), name='hstocks_create'),
    url(r'^orders/create$', views.OrdersCreateView.as_view(), name='orders_create'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^analysis/$', views.analysis, name='analysis'),
]

