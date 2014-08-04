# -*- coding: utf-8 -*-
from django.db.models.query_utils import Q
from django_filters import FilterSet, ModelMultipleChoiceFilter
from django_filters.filters import Filter
from djangocms_news.models import NewsItem, NewsCategory


def news_category(qs, value):
    terms = value.split(',')
    f = None
    for term in terms:
        if f is None:
            f = Q(news_categories__id=term)
        else:
            f = f |\
                Q(news_categories__id=term)

    return qs.filter(f)


class NewsItemFilter(FilterSet):
    category = Filter(action=news_category)

    class Meta:
        model = NewsItem
        fields = ['category']
