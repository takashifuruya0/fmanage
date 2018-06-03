# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
from . import views    

app_name = 'account'
urlpatterns = [
# Login, logout
    url(r'^login$', auth_views.login, {'template_name': 'account/login.html'}, name='login'),
    url(r'^logout$', auth_views.logout, name='logout'),
]
