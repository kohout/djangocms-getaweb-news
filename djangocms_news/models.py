from cms.models.pluginmodel import CMSPlugin
from cms.models.pagemodel import Page
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.timezone import utc
from django.views.generic import TemplateView
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
from tinymce.models import HTMLField
import datetime

class NewsCategory(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name=_(u'Title'))

    def newsitems_count(self):
        return self.newsitem_set.filter(active=True).count()

    newsitems_count.short_description = _(u'Count of active news items')

    def get_absolute_url(self):
        return reverse('news-detail', kwargs={'category': self.pk})

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u'News Category')
        verbose_name_plural = _(u'News Categories')


class NewsItem(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_(u'Created at'))

    active = models.BooleanField(
        default=False,
        verbose_name=_(u'Active'))

    news_date = models.DateTimeField(
        verbose_name=_(u'Date of the Article'))

    title = models.CharField(
        max_length=150,
        verbose_name=_(u'Headline of the news article'))

    slug = models.SlugField(
        max_length=255,
        db_index=True,
        unique=True,
        verbose_name=_("slug"))

    abstract = models.TextField(
        blank=True,
        default='',
        verbose_name=_(u'Abstract of this news article'))

    content = HTMLField(
        blank=True,
        verbose_name=_(u'Content'))

    news_categories = models.ManyToManyField(
        NewsCategory,
        verbose_name=_(u'Selected news categories'))

    target_page = models.ForeignKey(Page,
        verbose_name=_(u'Target Page'))

    def get_first_image(self):
        images = self.newsimage_set.all()
        if images.count() == 0:
            return None
        first_image = images[0]
        return first_image

    def get_more_images(self):
        return self.newsimage_set.all()[1:]

    def has_multiple_images(self):
        return self.newsimage_set.count() > 1

    class Meta:
        ordering = ('-news_date', )
        verbose_name = _(u'News Item')
        verbose_name_plural = _(u'News Items')


class NewsTeaser(CMSPlugin):
    NEWS_ORDERING_FUTURE_ASC = 'future_asc'
    NEWS_ORDERING_PAST_DESC = 'past_desc'

    NEWS_ORDERING_CHOICES = (
        (NEWS_ORDERING_FUTURE_ASC, _(u'from now to future (ascending)')),
        (NEWS_ORDERING_PAST_DESC, _(u'from now to past (descending)')),
    )
    title = models.CharField(
        max_length=150,
        verbose_name=_(u'Headline of the news list'))

    news_categories = models.ManyToManyField(
        NewsCategory,
        verbose_name=_(u'Selected news categories'))

    ordering = models.CharField(
        max_length=20,
        choices=NEWS_ORDERING_CHOICES,
        default=NEWS_ORDERING_PAST_DESC,
        verbose_name=_(u'Ordering/Selection of Articles'))

    target_page = models.ForeignKey(Page,
        verbose_name=_(u'Target Page'))

    def get_items(self):
        items = NewsItem.objects.filter(active=True)
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.ordering == self.NEWS_ORDERING_PAST_DESC:
            items = items.filter(news_date__lte=now).order_by('-news_date')
        else:
            items = items.filter(news_date__gte=now).order_by('news_date')
        return items

    def __unicode__(self):
        return self.title


class NewsImage(models.Model):
    image = ThumbnailerImageField(
        upload_to='news_image/',
        verbose_name=_(u'Image'))

    image_width = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        verbose_name=_(u'Original Image Width'))

    image_height = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        verbose_name=_(u'Original Image Height'))

    title = models.CharField(
        blank=True,
        default='',
        max_length=150,
        verbose_name=_(u'Image Title'))

    alt = models.CharField(
        blank=True,
        default='',
        max_length=150,
        verbose_name=_(u'Alternative Image Text'))

    ordering = models.PositiveIntegerField(
        verbose_name=_(u'Ordering'))

    news_item = models.ForeignKey(NewsItem,
        verbose_name=_(u'News Item'))

    def get_title(self):
        if self.title:
            return self.title
        return self.news_item.title

    def get_alt(self):
        if self.alt:
            return self.alt
        return u'Bild %s' % (self.ordering + 1)

    #def save(self):
    #    if self.ordering is None:
    #        self.ordering = self.news_item.newsimage_set.count()
    #    super(NewsImage, self).save()

    def _get_image(self, image_format):
        _image_format = settings.THUMBNAIL_ALIASES[''][image_format]
        _img = self.image
        try:
            img = get_thumbnailer(_img).get_thumbnail(_image_format)
            return {
                'url': img.url,
                'width': img.width,
                'height': img.height,
                'alt': self.alt,
                'title': self.title,
            }
        except (UnicodeEncodeError, InvalidImageFormatError):
            return None

    def get_preview(self):
        return self._get_image('preview')

    def get_teaser(self):
        return self._get_image('teaser')

    def get_normal(self):
        return self._get_image('normal')

    def get_main(self):
        return self._get_image('main')

    def get_fullsize(self):
        return self._get_image('fullsize')

    def __unicode__(self):
        if self.title:
            return self.title
        if self.alt:
            return self.alt
        return _(u'Image #%s') % self.ordering

    class Meta:
        ordering = ['ordering']
        verbose_name = _(u'News Image')
        verbose_name_plural = _(u'News Images')
