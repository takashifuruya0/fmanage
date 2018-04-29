# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
from . import views    

app_name = 'kakeibo'
urlpatterns = [
    url(r'^updates$', views.updates, name='update'),
    
    # redirect_to_form
    url(r'^form$', views.redirect_form, name='form'),
    url(r'^sharedform$', views.redirect_sharedform, name='shared_form'),
    # mine
    url(r'^mine$', views.mine, name='mine'),
    url(r'^mine/(\d{4})(\d{2})$', views.mine_month, name='mine_month'),
    # credit
    url(r'^credit$', views.credit, name='credit'),
    # shared
    url(r'^shared$', views.shared, name='shared'),
    url(r'^shared/(\d{4})(\d{2})$', views.shared_month, name='shared_month'),
    # dashboard
    url(r'^$', views.dashboard, name='dashboard'),

    # test
    url(r'^test$', views.test, name='test'),

    # figure
    url(r'^fig/bars_balance$', views.bars_balance, name='bars_balance'),
    url(r'^fig/pie_expense$', views.pie_epense, name='pie_expense')
]

