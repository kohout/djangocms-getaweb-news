# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tinymce.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name='Titel')),
            ],
            options={
                'verbose_name': 'News Category',
                'verbose_name_plural': 'News Categories',
            },
        ),
        migrations.CreateModel(
            name='NewsImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to=b'cms_news/', verbose_name='Bild')),
                ('image_width', models.PositiveSmallIntegerField(default=0, null=True, verbose_name='Original Image Width')),
                ('image_height', models.PositiveSmallIntegerField(default=0, null=True, verbose_name='Original Image Height')),
                ('title', models.CharField(default=b'', max_length=150, verbose_name='Image Title', blank=True)),
                ('alt', models.CharField(default=b'', max_length=150, verbose_name='Alternative Image Text', blank=True)),
                ('ordering', models.PositiveIntegerField(verbose_name='Ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name': 'News Image',
                'verbose_name_plural': 'News Images',
            },
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('active', models.BooleanField(default=False, verbose_name='Aktiv')),
                ('news_date', models.DateTimeField(verbose_name='Date of the Article')),
                ('title', models.CharField(max_length=150, verbose_name='Headline of the news article')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('abstract', models.TextField(default=b'', verbose_name='Abstract of this news article', blank=True)),
                ('content', tinymce.models.HTMLField(null=True, verbose_name='Inhalt', blank=True)),
                ('price', models.TextField(null=True, verbose_name='Highlighted price', blank=True)),
                ('youtube_id', models.TextField(null=True, verbose_name='ID of embedded youtube video', blank=True)),
                ('additional_images_pagination', models.PositiveIntegerField(default=1, verbose_name='Pagination of additional images', choices=[(0, 'No pagination'), (1, 'Pagination'), (2, 'Slideshow')])),
                ('additional_images_speed', models.PositiveIntegerField(default=3000, help_text='This option is relevant, if you choose the slideshow-mode', verbose_name='Speed of transition')),
                ('tags', models.TextField(null=True, verbose_name='Tags', blank=True)),
                ('news_categories', models.ManyToManyField(to='djangocms_news.NewsCategory', verbose_name='Selected news categories', blank=True)),
                ('target_page', models.ManyToManyField(to='cms.Page', verbose_name='Target Page')),
            ],
            options={
                'ordering': ('-news_date',),
                'verbose_name': 'News Item',
                'verbose_name_plural': 'News Items',
            },
        ),
        migrations.CreateModel(
            name='NewsTeaser',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=150, verbose_name='Headline of the news list')),
                ('ordering', models.CharField(default=b'past_desc', max_length=20, verbose_name='Ordering/Selection of Articles', choices=[(b'future_asc', 'from now to future (ascending)'), (b'past_desc', 'from now to past (descending)')])),
                ('news_categories', models.ManyToManyField(to='djangocms_news.NewsCategory', verbose_name='Selected news categories', blank=True)),
                ('target_page', models.ForeignKey(verbose_name='Target Page', to='cms.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AddField(
            model_name='newsimage',
            name='news_item',
            field=models.ForeignKey(verbose_name='News Item', to='djangocms_news.NewsItem'),
        ),
    ]
