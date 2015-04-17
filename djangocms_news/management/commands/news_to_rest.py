# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import slumber

class Command(BaseCommand):
    help = u'For testing'

    def handle(self, *args, **options):
        url = 'http://localhost:8001/news-api/'
        api = slumber.API(url, auth=('user', 'user'))
        news_list = api.news.get()
        print news_list['results']
