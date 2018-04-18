# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
from . import views    

app_name = 'kakeibo'
urlpatterns = [
    url(r'^dashboard$', views.dashboard, name='dashboard'),
]

