"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.views.static import serve
from django.conf.urls import url
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditorView

from website import settings
from DBModel import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^detail$', views.detail),
    url(r'^userinfo$', views.userinfo),
    url(r'^release$', views.release),
    url(r'^reqinfo$', views.reqinfo),
    url(r'^toollist$', views.toollist),
    url(r'^articlelist$', views.articlelist),
    url(r'^article$', views.article),
    url(r'^pytoolsip/media/(?P<path>.*)', serve, {"document_root":settings.MEDIA_ROOT}),
    url(r'^ckeditor/upload/', views.checkLogined(ckeditorView.upload), name='ckeditor_upload'),
    url(r'^ckeditor/browse/', never_cache(views.checkLogined(ckeditorView.browse)), name='ckeditor_browse'),
]