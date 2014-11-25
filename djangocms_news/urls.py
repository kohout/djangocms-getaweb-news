from django.conf.urls import patterns, include, url
from .views import NewsListView, NewsDetailView

urlpatterns = patterns('',
    url(r'^news/(?P<slug>[\w-]+)/$',
        NewsDetailView.as_view(),
        name='news-detail'),
    url(r'^$',
        NewsListView.as_view(),
        name='news-index'),
)
