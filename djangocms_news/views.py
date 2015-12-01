# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import resolve
from django.db.models.query_utils import Q
from django.views.generic import ListView, DetailView, UpdateView

from .forms import UploadForm
from .filters import NewsItemFilter
from .models import NewsItem, NewsCategory, NewsImage, \
    remote_publishing_slave, remote_publishing_master


class NewsMixin(object):
    current_category = 0
    current_page = None

    def get_current_page(self):
        if self.current_page:
            return self.current_page
        self.current_page = self.request.current_page
        if self.current_page.publisher_is_draft:
            self.current_page = self.current_page.publisher_public
        return self.current_page

    def get_queryset(self):
        if self.request.toolbar.edit_mode == True:
            q = NewsItem.objects.all()
        else:
            q = NewsItem.objects.filter(active=True)
        # target page
        if self.request.user.is_staff or self.request.user.is_superuser:
            # regard public and private version
            q = q.filter(
                Q(target_page=self.request.current_page) |
                Q(target_page=self.request.current_page.publisher_public))
        else:
            # regard only public version
            q = q.filter(target_page=self.request.current_page)

        if remote_publishing_master():
            q = q.filter(remote_publishing__icontains='localhost')

        #self.current_category = int(self.kwargs.get('category', 0))
        #if self.current_category > 0:
        #    q = q.filter(news_categories__in=[self.current_category])
        return q

    def get_news_categories(self):
        news_categories = NewsCategory.objects.filter(
            newsitem__target_page=self.get_current_page()
        ).distinct().order_by('title')
        return [{
            'item': n,
            'count': n.newsitem_set.count(),
            'selected': n.id == self.current_category,
        } for n in news_categories]

    def get_context_data(self, *args, **kwargs):
        ctx = super(NewsMixin, self).get_context_data(*args, **kwargs)
        ctx['current_app'] = resolve(self.request.path_info).namespace
        ctx['categories'] = self.get_news_categories()
        if 'category' in self.kwargs:
            ctx['category'] = self.kwargs['category']
        return ctx


class NewsListView(NewsMixin, ListView):
    """
    A complete list of the news items
    """
    model = NewsItem
    template_name = 'djangocms_news/news_index.html'
    paginate_by = 25
    filter_class = NewsItemFilter

    def __init__(self):
        self.paginate_by = getattr(settings, 'NEWS_PAGINATE_BY', 25)
        super(NewsListView, self).__init__()

    def get_queryset(self):
        q = super(NewsListView, self).get_queryset()
        return self.filter_class(self.request.GET, q)

    def get_context_data(self, *args, **kwargs):
        ctx = super(NewsListView, self).get_context_data(*args, **kwargs)
        ctx['model'] = self.model
        if self.request.GET.get('category'):
            filter_categories = self.request.GET.get('category')
            filter_categories = filter_categories.split(',')
            ctx['filter_categories'] = filter_categories
        else:
            ctx['show_all'] = True
        return ctx


class NewsUploadView(UpdateView):
    model = NewsItem
    form_class = UploadForm
    template_name = 'djangocms_news/upload.html'

    def form_valid(self, form):
        for uploaded_file in form.cleaned_data['attachments']:
            img = NewsImage()
            img.news_item = self.object
            img.ordering = self.object.newsimage_set.count()
            img.image = uploaded_file
            img.save()
        return super(NewsUploadView, self).form_valid(form)


class NewsDetailView(NewsMixin, DetailView):
    """
    Detail view of a news item
    """
    slug_field = 'slug'
    model = NewsItem
    template_name = 'djangocms_news/news_detail.html'

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


try:
    from rest_framework import viewsets
    from .serializers import NewsSerializer, NewsImageSerializer

    class NewsViewSet(viewsets.ModelViewSet):
        queryset = NewsItem.objects.all()
        serializer_class = NewsSerializer
        lookup_field = 'remote_id'

    class NewsImageViewSet(viewsets.ModelViewSet):
        queryset = NewsImage.objects.all()
        serializer_class = NewsImageSerializer
        lookup_field = 'remote_id'
except ImportError:
    pass
