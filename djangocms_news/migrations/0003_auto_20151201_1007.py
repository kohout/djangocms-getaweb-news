# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_news', '0002_auto_20151201_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsitem',
            name='additional_images_pagination',
            field=models.PositiveIntegerField(default=0, verbose_name='Pagination of additional images', choices=[(0, 'No pagination'), (1, 'Pagination'), (2, 'Slideshow')]),
        ),
    ]
