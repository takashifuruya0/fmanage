# coding:utf-8
from django.conf.urls import url
from django.urls import path
from django.contrib.auth.decorators import login_required
from kakeibo.views import views_figure, views_list, views_detail, views_create, views_delete
from kakeibo.views import views_main as views
from kakeibo.views import views_redirect as views_redirect
# django-rest-framework
from rest_framework import routers
from kakeibo.views.views_drm import UsagesViewSet, ResourcesViewSet, KakeibosViewSet
from kakeibo.views.views_drm import SharedKakeibosViewSet, CreditItemsViewSet, CreditsViewSet
from kakeibo.views.views_drm import CronKakeiboViewSet, CronSharedViewSet, UsualRecordViewSet


app_name = 'kakeibo'
urlpatterns = [
    
    # redirect_to_link
    url(r'^metabase/$', views_redirect.redirect_metabase, name='metabase'),
    url(r'^knowledge/$', views_redirect.redirect_knowledge, name='knowledge'),
    # mine
    url(r'^mine/$', views.mine, name='mine'),
    # credit
    url(r'^credit/$', views.credit, name='credit'),
    # shared
    url(r'^shared/$', views.shared, name='shared'),
    # dashboard
    url(r'^$', views.dashboard, name='dashboard'),
    # create
    url(r'^mine/create/$', views_create.KakeiboCreate.as_view(), name="kakeibo_create"),
    url(r'^shared/create/$', views_create.SharedCreate.as_view(), name="shared_create"),
    url(r'^event/create/$', views_create.EventCreate.as_view(), name="event_create"),
    # list
    url(r'^usage/list/$', login_required(views_list.UsageList.as_view()), name="usage_list"),
    url(r'^mine/list/$', login_required(views_list.KakeiboList.as_view()), name="kakeibo_list"),
    url(r'^shared/list/$', views_list.SharedList.as_view(), name="shared_list"),
    url(r'^credit/list/$', login_required(views_list.CreditList.as_view()), name="credit_list"),
    url(r'^credit/items/list/$', login_required(views_list.CreditItemList.as_view()), name="credit_item_list"),
    url(r'^event/list/$', views_list.EventList.as_view(), name="event_list"),
    # detail
    url(r'^usage/detail/(?P<pk>\d+)/$', login_required(views_detail.UsageDetail.as_view()), name="usage_detail"),
    url(r'^mine/detail/(?P<pk>\d+)/$', login_required(views_detail.KakeiboDetail.as_view()), name="kakeibo_detail"),
    url(r'^shared/detail/(?P<pk>\d+)/$', views_detail.SharedDetail.as_view(), name="shared_detail"),
    url(r'^credit/detail/(?P<pk>\d+)/$', login_required(views_detail.CreditDetail.as_view()), name="credit_detail"),
    url(r'^credit/items/detail/(?P<pk>\d+)/$', login_required(views_detail.CreditItemDetail.as_view()), name="credit_item_detail"),
    path('event/detail/<int:pk>/', login_required(views_detail.EventDetail.as_view()), name="event_detail"),
    # update
    url(r'^mine/update/(?P<pk>\d+)/$', login_required(views_detail.KakeiboUpdate.as_view()), name="kakeibo_update"),
    url(r'^shared/update/(?P<pk>\d+)/$', views_detail.SharedUpdate.as_view(), name="shared_update"),
    url(r'^usage/update/(?P<pk>\d+)/$', login_required(views_detail.UsageUpdate.as_view()), name="usage_update"),
    url(r'^credit/update/(?P<pk>\d+)/$', login_required(views_detail.CreditUpdate.as_view()), name="credit_update"),
    url(r'^credit/items/update/(?P<pk>\d+)/$', login_required(views_detail.CreditItemUpdate.as_view()), name="credit_item_update"),
    url(r'^event/update/(?P<pk>\d+)/$', login_required(views_detail.EventUpdate.as_view()), name="event_update"),
    # delete
    path("mine/detail/<int:pk>/delete", views_delete.KakeiboDelete.as_view(), name="kakeibo_delete"),
    path("shared/detail/<int:pk>/delete", views_delete.SharedDelete.as_view(), name="shared_delete"),
    # link_kakeibo_and_credit
    url(r'^link$', views.link_kakeibo_and_credit, name='link_kakeibo_and_credit'),
    # Process
    path("read_csv", views.ReadCSVView.as_view(), name="read_csv"),
    path("usual_record", views.UsualRecordView.as_view(), name="usual_record"),

    # test
    url(r'^test$', views.test, name='test'),

    # figure
    # 資産内訳（今月と先月）
    url(r'^fig/bars_resource$', views_figure.bars_resource, name='bars_resource'),
    # 収支
    url(r'^fig/bars_balance$', views_figure.bars_balance, name='bars_balance'),
    # 月末精算
    url(r'^fig/bars_shared_eom$', views_figure.bars_shared_eom, name='bars_shared_eom'),
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
    # test
    url(r'^fig/test$', views_figure.test_figure, name='testfig'),
]

router = routers.DefaultRouter()
router.register(r'kakeibo/usage', UsagesViewSet)
router.register(r'kakeibo/resource', ResourcesViewSet)
router.register(r'kakeibo/kakeibo', KakeibosViewSet)
router.register(r'kakeibo/shared', SharedKakeibosViewSet)
router.register(r'kakeibo/credit', CreditsViewSet)
router.register(r'kakeibo/credititem', CreditItemsViewSet)
router.register(r'kakeibo/cron/kakeibo', CronKakeiboViewSet)
router.register(r'kakeibo/cron/shared', CronSharedViewSet)
router.register(r'kakeibo/usualrecord', UsualRecordViewSet)

