"""fmanage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import include, path            # includeを追加
from django.contrib import admin
# media
from django.conf import settings
from django.views.static import serve
from django.views.generic import RedirectView
# django-rest-framework
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from asset.urls import router as asset_router
from kakeibo.urls import router as kakeibo_router
from lancers.urls import router as lancers_router
# accounts
from accounts.views import UserDetailAPIView

router = routers.DefaultRouter()
# router.registry.extend(asset_router.registry)
router.registry.extend(kakeibo_router.registry)
router.registry.extend(lancers_router.registry)


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='kakeibo/')),
    url(r'^admin/', admin.site.urls),
    url(r'^kakeibo/', include('kakeibo.urls', namespace='kakeibo')),
    url(r'^asset/', include('asset.urls', namespace='asset')),
    url(r'^api/', include('api.urls', namespace='api')),
    path('accounts/', include('allauth.urls')),
    # url(r'^account/', include('accounts.urls', namespace='account')),
    url(r'^nams/', include('web.urls', namespace='web')),
    url(r'^document/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('lancers/', include('lancers.urls'), name='lancers'),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/user-detail/', UserDetailAPIView.as_view()),
    url(r'^drm/', include(router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append(path('docs/', include_docs_urls(title='FK-MANAGEMENT API')))
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
