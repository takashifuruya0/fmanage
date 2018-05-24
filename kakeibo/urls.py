# coding:utf-8                                                                  
                                                                                
from django.conf.urls import url                                                
from django.contrib.auth import views as auth_views                             
                                                                                
#from . import views    
from kakeibo.views import views_figure, views_list
from kakeibo.views import views_main as views

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
    url(r'^mine/list$', views_list.KakeiboList.as_view(), name="kakeibo_list"),
    url(r'^shared/list$', views_list.SharedList.as_view(), name="shared_list"),

    # test
    url(r'^test$', views.test, name='test'),

    # figure
    # 資産内訳（今月と先月）
    url(r'^fig/bars_resource$', views_figure.bars_resource, name='bars_resource'),
    # 収支
    url(r'^fig/bars_balance$', views_figure.bars_balance, name='bars_balance'),
    # 円
    url(r'^fig/pie_expense$', views_figure.pie_expense, name='pie_expense'),
    url(r'^fig/pie_resource$', views_figure.pie_resource, name='pie_resource'),
    url(r'^fig/pie_credititem$', views_figure.pie_credititem, name='pie_credititem'),
    url(r'^fig/pie_credit$', views_figure.pie_credit, name='pie_credit'),
    url(r'^fig/pie_shared$', views_figure.pie_shared, name='pie_shared'),
    url(r'^fig/pie_usage_cash$', views_figure.pie_usage_cash, name='pie_usage_cash'),
    url(r'^fig/pie_usage$', views_figure.pie_usage, name='pie_usage'),
    # 棒・線
    url(r'^fig/barline_usage$', views_figure.barline_usage, name='barline_usage'),
    url(r'^fig/barline_expense_cash$', views_figure.barline_expense_cash, name='barline_expense_cash'),
    # 線
    url(r'^fig/lines_usage_cash$', views_figure.lines_usage_cash, name='lines_usage_cash'),

]

