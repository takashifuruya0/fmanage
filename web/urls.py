# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from web.views import views_main, views_entry, views_order, views_stock, views_ajax
from web.views import views_api


app_name = 'web'
urlpatterns = [
    # dashboard
    path('', views_main.Main.as_view(), name='main'),
    path('investment/', views_main.Investment.as_view(), name='investment'),

    # entry
    path('entry/', views_entry.EntryList.as_view(), name='entry_list'),
    path('entry/create/', views_entry.EntryCreate.as_view(), name='entry_create'),
    path('entry/<int:pk>/', views_entry.EntryDetail.as_view(), name='entry_detail'),
    path('entry/<int:pk>/edit/', views_entry.EntryUpdate.as_view(), name='entry_edit'),
    path('entry/<int:pk>/delete/', views_entry.EntryDelete.as_view(), name='entry_delete'),
    # order
    path('order/', views_order.OrderList.as_view(), name="order_list"),
    path('order/create', views_order.OrderCreate.as_view(), name='order_create'),
    path('order/<int:order_id>/', views_order.OrderDetail.as_view(), name='order_detail'),
    path('order/<int:order_id>/edit/', views_order.OrderUpdate.as_view(), name='order_edit'),
    # stock
    path('stock/', views_stock.StockList.as_view(), name="stock_list"),
    path('stock/create/', views_stock.StockCreate.as_view(), name='stock_create'),
    path('stock/<stock_code>/', views_stock.StockDetail.as_view(), name='stock_detail'),
    path('stock/<stock_code>/edit/', views_stock.StockUpdate.as_view(), name='stock_edit'),
    # api
    path('api/create_order/', views_api.create_order, name="api_create_order"),
    path('api/get_current_vals/', views_api.GetCurrentVals.as_view(), name="api_get_current_vals"),
    path('api/receive_alert/', views_api.ReceiveAlert.as_view(), name="api_receive_alert"),
    path('api/slack_interactive/', views_api.SlackInteractive.as_view(), name="api_slack_interactive"),
    # ajax
    path('ajax/get_order/', views_ajax.GetOrder.as_view(), name='ajax_get_order'),
    path('ajax/set_alert/', views_ajax.SetAlert.as_view(), name='ajax_set_alert'),
    path('ajax/buy_order/', views_ajax.BuyOrder.as_view(), name='ajax_buy_order'),
    path('ajax/activate_entry/', views_ajax.ActivateEntry.as_view(), name='ajax_activate_entry'),
    path('ajax/deactivate_entry/', views_ajax.DeactivateEntry.as_view(), name='ajax_deactivate_entry'),
    path('ajax/get_stock_info/', views_ajax.GetStockInfo.as_view(), name='ajax_get_stock_info'),

]

