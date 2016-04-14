# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_news', '0003_auto_20151201_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsimage',
            name='alt',
            field=models.CharField(default=b'', max_length=150, verbose_name='Alternativer Bild-Text', blank=True),
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='image_height',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='H\xf6he des Originalbildes'),
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='image_width',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='Breite des Originalbildes'),
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='ordering',
            field=models.PositiveIntegerField(verbose_name='Sortierung'),
        ),
        migrations.AlterField(
            model_name='newsimage',
            name='title',
            field=models.CharField(default=b'', max_length=150, verbose_name='Bild-Title', blank=True),
        ),
    ]
