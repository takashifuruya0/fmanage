# coding:utf-8
# from django.conf.urls import url
from django.urls import include, path
from lancers.views import Main, OpportunityFormView


app_name = 'lancers'
urlpatterns = [
    # dashboard
    path('', Main.as_view(), name='main'),
    path('form/opportunity', OpportunityFormView.as_view(), name='form_opportunity'),
]

