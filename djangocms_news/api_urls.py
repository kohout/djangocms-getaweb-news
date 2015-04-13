from django.conf import settings
from django.conf.urls import patterns, include, url
from .views import NewsViewSet
from rest_framework import routers
from .models import remote_publishing_slave

if remote_publishing_slave():

    router = routers.DefaultRouter()
    router.register(r'news', NewsViewSet)

    urlpatterns = patterns('',
                            url(r'^', include(router.urls)),)

    print urlpatterns