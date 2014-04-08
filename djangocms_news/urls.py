from django.conf.urls import patterns, include, url
from .views import NewsListView, NewsDetailView

urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/$',
        NewsDetailView.as_view(),
        name='news-detail'),
    url(r'^category/(?P<category>[\w-]+)/$',
        NewsListView.as_view(),
        name='news-category'),
    url(r'^$',
        NewsListView.as_view(),
        name='news-index'),
)
