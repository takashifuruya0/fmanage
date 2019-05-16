# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url
from asset.views import views, views_ajax
# django-rest-framework
from rest_framework import routers
from asset.views.views_drm import OrdersViewSet, StocksViewSet, HoldingStocksViewSet, AssetStatusViewSet


app_name = 'asset'
urlpatterns = [
    # updates
    url(r'^$', views.asset_dashboard, name='dashboard'),
    url(r'^analysis/$', views.analysis_list, name='analysis_list'),
    url(r'^analysis/(?P<code>\d+)/$', views.analysis_detail, name='analysis_detail'),
    url(r'^ajax/$', views_ajax.ajax_get_stock_name, name='ajax'),
    url(r'^test/$', views.test, name="test"),
]

router = routers.DefaultRouter()
router.register(r'orders', OrdersViewSet)
router.register(r'stocks', StocksViewSet)
router.register(r'assetstatus', AssetStatusViewSet)
router.register(r'holdingstocks', HoldingStocksViewSet)

