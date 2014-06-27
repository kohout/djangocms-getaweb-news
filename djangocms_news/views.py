# -*- coding: utf-8 -*-
from django.db.models import Q
from django.core.urlresolvers import resolve
from django.views.generic import ListView, DetailView
from .models import NewsItem, NewsCategory

class NewsMixin(object):
    current_category = 0

    def get_queryset(self):
        q = NewsItem.objects.filter(active=True)
        if self.request.user.is_staff or self.request.user.is_superuser:
            # regard public and private version
            q = q.filter(
                Q(target_page=self.request.current_page) |
                Q(target_page=self.request.current_page.publisher_public))
        else:
            # regard only public version
            q = q.filter(target_page=self.request.current_page)

        self.current_category = int(self.kwargs.get('category', 0))
        if self.current_category > 0:
            q = q.filter(news_categories__in=[self.current_category])
        return q

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


class NewsDetailView(NewsMixin, DetailView):
    """
    Detail view of a news item
    """
    slug_field = 'slug'
    model = NewsItem
    template_name = 'djangocms_news/detail.html'

    def get_object(self):
        obj = super(NewsDetailView, self).get_object()
        categories = obj.news_categories.all()
        if categories.count() > 0:
            self.current_category = categories[0].id
        return obj

    def get_next(self):
        q = self.get_queryset().filter(
            news_date__lt=self.object.news_date).order_by('-news_date')
        if q.count() > 0:
            return q[0]
        return None

    def get_previous(self):
        q = self.get_queryset().filter(
            news_date__gt=self.object.news_date).order_by('news_date')
        if q.count() > 0:
            return q[0]
        return None

    def get_context_data(self, *args, **kwargs):
        ctx = super(NewsDetailView, self).get_context_data(*args, **kwargs)
        ctx['next'] = self.get_next()
        ctx['previous'] = self.get_previous()
        return ctx
