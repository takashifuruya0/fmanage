# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
from . import views    

app_name = 'api'
urlpatterns = [
    url(r'^kakeibo$', views.kakeibo, name='kakeibo'),
    url(r'^shared$', views.shared, name='shared'),
    url(r'^seisan$', views.seisan, name='seisan'),
    url(r'^kakeibo_month$', views.kakeibo_month, name="kakeibo_month"),
    url(r'^shared_month$', views.shared_month, name="shared_month"),
    url(r'^asset/order$', views.asset_order, name="asset_order"),
    url(r'^asset/status$', views.asset_status, name="asset_status"),
    url(r'^asset/holding$', views.asset_holding, name="asset_holding"),
    url(r'^asset$', views.asset, name="asset"),
    url(r'^test$', views.test, name="test"),
    url(r'^googlehome/shared$', views.googlehome_shared, name="googlehome_shared"),
]
