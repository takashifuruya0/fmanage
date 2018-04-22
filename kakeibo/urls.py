# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
from . import views    

app_name = 'kakeibo'
urlpatterns = [
    url(r'^updates$', views.updates, name='update'),
    url(r'^form$', views.redirect_form, name='form'),
    url(r'^$', views.dashboard, name='dashboard'),
]

