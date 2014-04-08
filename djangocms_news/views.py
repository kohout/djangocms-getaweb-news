# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView
from .models import NewsItem, NewsCategory
from django.core.urlresolvers import resolve


class NewsMixin(object):
    current_category = 0

    def get_queryset(self):
        return NewsItem.objects.filter(active=True,
            target_page=self.request.current_page)

    def get_news_categories(self):
        news_categories = NewsCategory.objects.filter(
            newsitem__target_page=self.request.current_page
        ).distinct().order_by('title')
        return [{
            'item': n,
            'count': n.newsitem_set.count(),
            'selected': n.id == self.current_category,
        } for n in news_categories]

    def get_context_data(self, *args, **kwargs):
        ctx = super(NewsMixin, self).get_context_data(*args, **kwargs)
        ctx['categories'] = self.get_news_categories()
        return ctx


class NewsListView(NewsMixin, ListView):
    """
    A complete list of the news items
    """
    model = NewsItem
    template_name = 'djangocms_news/list.html'

    def get_queryset(self):
        q = super(NewsListView, self).get_queryset()
        self.current_category = int(self.kwargs.get('category', 0))
        if self.current_category > 0:
            q = q.filter(news_categories__in=[self.current_category])
        return q


class NewsDetailView(NewsMixin, DetailView):
    """
    Detail view of a news item
    """
    slug_field = 'slug'
    model = NewsItem
    template_name = 'djangocms_news/detail.html'

    def get_object(self):
        obj = super(NewsDetailView, self).get_object()
        self.current_category = obj.news_categories.all()[0].id
        return obj
