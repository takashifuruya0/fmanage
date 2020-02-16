# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from web.views import views_main, views_entry, views_order, views_stock


app_name = 'web'
urlpatterns = [
    # dashboard
    path('', views_main.Main.as_view(), name='main'),
    path('investment/', views_main.Investment.as_view(), name='investment'),
    # entry
    path('entry/', views_entry.EntryList.as_view(), name='entry_list'),
    path('entry/create', views_entry.EntryCreate.as_view(), name='entry_create'),
    path('entry/<int:pk>/', views_entry.EntryDetail.as_view(), name='entry_detail'),
    path('entry/<int:pk>/edit', views_entry.EntryUpdate.as_view(), name='entry_edit'),
    # order
    path('order/', views_order.OrderList.as_view(), name="order_list"),
    path('order/<int:order_id>/', views_order.order_detail, name='order_detail'),
    path('order/<int:order_id>/edit', views_order.order_edit, name='order_edit'),
    # stock
    path('stock/$', views_stock.StockList.as_view(), name="stock_list"),
    path('stock/<stock_code>/', views_stock.stock_detail, name='stock_detail'),
    path('stock/<stock_code>/edit', views_stock.stock_edit, name='stock_edit'),
]

