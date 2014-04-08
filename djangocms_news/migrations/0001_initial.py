# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NewsCategory'
        db.create_table(u'djangocms_news_newscategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'djangocms_news', ['NewsCategory'])

        # Adding model 'NewsItem'
        db.create_table(u'djangocms_news_newsitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('news_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('abstract', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('content', self.gf('tinymce.models.HTMLField')()),
        ))
        db.send_create_signal(u'djangocms_news', ['NewsItem'])

        # Adding M2M table for field news_categories on 'NewsItem'
        m2m_table_name = db.shorten_name(u'djangocms_news_newsitem_news_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newsitem', models.ForeignKey(orm[u'djangocms_news.newsitem'], null=False)),
            ('newscategory', models.ForeignKey(orm[u'djangocms_news.newscategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['newsitem_id', 'newscategory_id'])

        # Adding model 'NewsTeaser'
        db.create_table(u'djangocms_news_newsteaser', (
            (u'cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('ordering', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'djangocms_news', ['NewsTeaser'])

        # Adding M2M table for field news_categories on 'NewsTeaser'
        m2m_table_name = db.shorten_name(u'djangocms_news_newsteaser_news_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newsteaser', models.ForeignKey(orm[u'djangocms_news.newsteaser'], null=False)),
            ('newscategory', models.ForeignKey(orm[u'djangocms_news.newscategory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['newsteaser_id', 'newscategory_id'])


    def backwards(self, orm):
        # Deleting model 'NewsCategory'
        db.delete_table(u'djangocms_news_newscategory')

        # Deleting model 'NewsItem'
        db.delete_table(u'djangocms_news_newsitem')

        # Removing M2M table for field news_categories on 'NewsItem'
        db.delete_table(db.shorten_name(u'djangocms_news_newsitem_news_categories'))

        # Deleting model 'NewsTeaser'
        db.delete_table(u'djangocms_news_newsteaser')

        # Removing M2M table for field news_categories on 'NewsTeaser'
        db.delete_table(db.shorten_name(u'djangocms_news_newsteaser_news_categories'))


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'djangocms_news.newscategory': {
            'Meta': {'object_name': 'NewsCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'djangocms_news.newsitem': {
            'Meta': {'ordering': "('-news_date',)", 'object_name': 'NewsItem'},
            'abstract': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('tinymce.models.HTMLField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'news_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['djangocms_news.NewsCategory']", 'symmetrical': 'False'}),
            'news_date': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'djangocms_news.newsteaser': {
            'Meta': {'object_name': 'NewsTeaser', '_ormbases': ['cms.CMSPlugin']},
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'news_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['djangocms_news.NewsCategory']", 'symmetrical': 'False'}),
            'ordering': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        }
    }

    complete_apps = ['djangocms_news']