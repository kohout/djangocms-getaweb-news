# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from .models import NewsCategory, NewsItem, NewsImage
from .forms import NewsItemForm

class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'newsitems_count', )

class NewsImageInline(admin.TabularInline):
    fields = ('render_preview', 'image', 'title', 'alt', 'ordering', )
    readonly_fields = ('render_preview', )
    model = NewsImage
    extra = 0
    sortable_field_name = 'ordering'

    def render_preview(self, news_image):
        url = news_image.image['preview'].url
        if url:
            return u'<img src="%s">' % url
        else:
            return u''

    render_preview.allow_tags = True
    render_preview.short_description = _(u'Preview')

class NewsItemAdmin(admin.ModelAdmin):
    form = NewsItemForm
    list_display = ('render_preview', 'title', 'news_date', 'active', )
    list_display_links = ('render_preview', 'title', 'news_date', )
    readonly_fields = ('render_preview', )
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (_(u'Common'), {
            'classes': ('grp-collapse grp-open', ),
            'fields': (
                ('active', ),
                ('news_date', ),
                ('target_page', 'news_categories', )
            )
        }),
        (_(u'Content'), {
            'classes': ('grp-collapse grp-open', ),
            'fields': ('title', 'slug', 'abstract', 'content', )
        })
    )
    inlines = [NewsImageInline]

    raw_id_fields = ('news_categories', )
    autocomplete_lookup_fields = {
        'm2m': ['news_categories'],
    }

    def render_preview(self, news_item):
        news_image = news_item.get_first_image()
        if not news_image:
            return u''

        url = news_image.image['preview'].url
        if not url:
            return u''

        return u'<img src="%s">' % url

    render_preview.allow_tags = True
    render_preview.short_description = _(u'Preview')

admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(NewsItem, NewsItemAdmin)
