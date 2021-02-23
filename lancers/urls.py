# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from lancers.views import Main, OpportunityFormView, SyncToProdView, MentaFormView
# django-rest-framework
from rest_framework import routers
from lancers.views import ClientViewSet, CategoryViewSet, OpportunityViewSet, OpportunityWorkViewSet


app_name = 'lancers'
urlpatterns = [
    # dashboard
    path('', Main.as_view(), name='main'),
    path('form/opportunity', OpportunityFormView.as_view(), name='form_opportunity'),
    path('form/menta', MentaFormView.as_view(), name='form_menta'),
    path('sync', SyncToProdView.as_view(), name='sync'),
]

router = routers.DefaultRouter()
router.register(r'lancers/client', ClientViewSet)
router.register(r'lancers/category', CategoryViewSet)
router.register(r'lancers/opportunity', OpportunityViewSet)
router.register(r'lancers/opportunitywork', OpportunityWorkViewSet)
