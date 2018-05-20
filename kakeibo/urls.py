# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
from . import views    

app_name = 'kakeibo'
urlpatterns = [
    # updates
    url(r'^updates$', views.updates, name='update'),
    url(r'^updates/shared$', views.updates_shared, name='update_shared'),
    
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
    # list
    url(r'^mine/list$', views.KakeiboList.as_view(), name="kakeibo_list"),
    url(r'^shared/list$', views.SharedList.as_view(), name="shared_list"),

    # test
    url(r'^test$', views.test, name='test'),

    # figure
    url(r'^fig/bars_balance$', views.bars_balance, name='bars_balance'),
    url(r'^fig/pie_expense$', views.pie_expense, name='pie_expense'),
    url(r'^fig/pie_expense$', views.pie_expense, name='pie_expense'),
    url(r'^fig/pie_resource$', views.pie_resource, name='pie_resource'),
    url(r'^fig/pie_credititem$', views.pie_credititem, name='pie_credititem'),
    url(r'^fig/pie_credit$', views.pie_credit, name='pie_credit'),
    url(r'^fig/pie_shared$', views.pie_shared, name='pie_shared'),
    url(r'^fig/barline_usage/(\d+)$', views.barline_usage, name='barline_usage'),
    url(r'^fig/bars_resource$', views.bars_resource, name='bars_resource'),

    url(r'^fig/lines_usage_cash/(\d{4})/(\d{1,2})$', views.lines_usage_cash, name='lines_usage_cash'),
    url(r'^fig/pie_usage_cash$', views.pie_usage_cash, name='pie_usage_cash'),
]

