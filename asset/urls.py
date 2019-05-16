# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url
from . import views
# django-rest-framework
from rest_framework import routers
from .views import OrdersViewSet, StocksViewSet


app_name = 'asset'
urlpatterns = [
    # updates
    url(r'^$', views.asset_dashboard, name='dashboard'),
    url(r'^stocks/create$', views.StocksCreateView.as_view(), name='stocks_create'),
    url(r'^hstocks/create$', views.HoldingStocksCreateView.as_view(), name='hstocks_create'),
    url(r'^orders/create$', views.OrdersCreateView.as_view(), name='orders_create'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^analysis/$', views.analysis_list, name='analysis_list'),
    url(r'^analysis/(?P<code>\d+)/$', views.analysis_detail, name='analysis_detail'),
    url(r'^test/$', views.test, name="test"),
]

router = routers.DefaultRouter()
router.register(r'orders', OrdersViewSet)
router.register(r'stocks', StocksViewSet)
