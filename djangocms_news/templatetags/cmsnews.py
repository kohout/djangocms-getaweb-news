# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from djangocms_news.resolvers import reverse

register = template.Library()


def render_img(img):
    return u'<img src="%(url)s" width="%(width)s" height="%(height)s" ' \
        u'title="%(title)s" alt="%(alt)s">' % img


@register.filter()
def image(value, image_format):
    if not value:
        return u''

    return mark_safe(render_img(value._get_image(image_format)))


@register.filter()
def image_url(value, image_format):
    if not value:
        return u''

    return value._get_image(image_format)['url']


@register.simple_tag()
def more_images(news_item, image_format):
    images = news_item.get_more_images()
    return [n._get_image(image_format) for n in images.all()]


@register.simple_tag(takes_context=True)
def newsindex_url(context, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'news-index')


@register.simple_tag(takes_context=True)
def newsitem_url(context, slug, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'news-detail', kwargs={
        'slug': slug})

@register.simple_tag(takes_context=True)
def newsupload_url(context, slug, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'news-upload',
        kwargs={'slug': slug})

@register.simple_tag(takes_context=True)
def newscategory_url(context, get, prefix=None, app_name=None):
    return "%s?category=%s" % (reverse(context['request'], prefix, app_name, 'news-index'), get)

@register.simple_tag(takes_context=True)
def page_pagination(context, category=None, page=1, prefix=None, app_name=None):
    if category:
        return "%s?category=%s&page=%s" % (reverse(context['request'], prefix, app_name, 'news-index'), category, page)
    else:
        return "%s?page=%s" % (reverse(context['request'], prefix, app_name, 'news-index'), page)
