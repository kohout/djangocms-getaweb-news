from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns, url
from .views import NewsListView, NewsDetailView, NewsUploadView

urlpatterns = patterns('',
    # public views
    url(r'^news/(?P<slug>[\w-]+)/$',
        NewsDetailView.as_view(),
        name='news-detail'),
    url(r'^$',
        NewsListView.as_view(),
        name='news-index'),

    # protected views
    url(r'^news/(?P<slug>[\w-]+)/upload/$',
        staff_member_required(NewsUploadView.as_view()),
        name='news-upload'),
)
