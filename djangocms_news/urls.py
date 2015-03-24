from django.conf import settings
from django.conf.urls import patterns, include, url
from .views import NewsListView, NewsDetailView, NewsViewSet
from rest_framework import routers, serializers, viewsets

router = routers.DefaultRouter()
router.register(r'news', NewsViewSet)

urlpatterns = patterns('',
    url(r'^news/(?P<slug>[\w-]+)/$',
        NewsDetailView.as_view(),
        name='news-detail'),
    url(r'^$',
        NewsListView.as_view(),
        name='news-index'),
)

if hasattr(settings, 'NEWS_REMOTE_PUBLISHING')\
        and settings.NEWS_REMOTE_PUBLISHING is True\
        and hasattr(settings, 'NEWS_REMOTE_ROLE')\
        and settings.NEWS_REMOTE_ROLE is 'SLAVE':

    router = routers.DefaultRouter()
    router.register(r'news', NewsViewSet)

    urlpatterns += patterns('',
                            url(r'^', include(router.urls)),
                            )

    #urlpatterns += patterns('',
    #                        url(r'^', include(router.urls)),
    #                        #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #                        )

    print urlpatterns