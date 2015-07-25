# -*- coding: utf-8 -*-
from rest_framework import serializers
from djangocms_news.models import NewsItem, NewsImage

class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage

class NewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsItem
        lookup_field = 'remote_id'
        fields = (
            'pk',
            'title',
            'slug',
            'active',
            'abstract',
            'content',
            'news_date',
            'additional_images_pagination',
            'additional_images_speed',
            'remote_id',
            'remote_target_pages',
        )
