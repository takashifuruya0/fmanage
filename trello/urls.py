# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url
                                                                                
from . import views    

app_name = 'api'
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
]
