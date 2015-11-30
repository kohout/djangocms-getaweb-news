from cms.models.pluginmodel import CMSPlugin
from cms.models.pagemodel import Page
from django.conf import settings
from .fields import MultiSelectField
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.utils.timezone import utc
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.signal_handlers import generate_aliases_global
from easy_thumbnails.signals import saved_file
from tinymce.models import HTMLField
import datetime

try:
    import slumber
except ImportError:
    slumber = None


saved_file.connect(generate_aliases_global)


def remote_publishing():
    """
    Wrapper function to determine whether remote publishing is activated or not

    :return: Boolean
    """
    return hasattr(settings, 'NEWS_REMOTE_PUBLISHING')


def remote_publishing_master():
    """
    Wrapper function to determine role.
    Returns false if remote publishing is not activated

    :return: Boolean
    """
    return remote_publishing() and hasattr(settings, 'NEWS_REMOTE_ROLE') \
        and settings.NEWS_REMOTE_ROLE is 'MASTER'


def remote_publishing_slave():
    """
    Wrapper function to determine role.
    Returns false if remote publishing is not activated

    :return: Boolean
    """
    return remote_publishing() and hasattr(settings, 'NEWS_REMOTE_ROLE') \
        and settings.NEWS_REMOTE_ROLE is 'SLAVE'


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
    ADDITIONAL_IMAGES_PAGINATION_CHOICES = (
        (0, _(u'No pagination')),
        (1, _(u'Pagination')),
        (2, _(u'Slideshow')),
    )

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
        blank=True, null=True,
        verbose_name=_(u'Content'))

    news_categories = models.ManyToManyField(
        NewsCategory,
        blank=True,
        verbose_name=_(u'Selected news categories'))

    target_page = models.ManyToManyField(
        Page,
        verbose_name=_(u'Target Page'))

    price = models.TextField(
        blank=True, null=True,
        verbose_name=_(u'Highlighted price'))

    youtube_id = models.TextField(
        blank=True, null=True,
        verbose_name=_(u'ID of embedded youtube video'))

    additional_images_pagination = models.PositiveIntegerField(
        default=1,
        choices=ADDITIONAL_IMAGES_PAGINATION_CHOICES,
        verbose_name=_(u'Pagination of additional images'))

    additional_images_speed = models.PositiveIntegerField(
        default=3000,
        help_text=_(
            u'This option is relevant, if you choose the slideshow-mode'),
        verbose_name=_(u'Speed of transition'))

# region remote_publishing
    if remote_publishing_slave() or remote_publishing_master():
        remote_id = models.CharField(max_length=100,
            blank=True, null=True,
            db_index=True)
        remote_publishing = MultiSelectField(
            blank=True, null=True,
            default='',
            choices=settings.NEWS_REMOTE_PUBLISHING_CHOICES,
            max_length=10000,
            verbose_name=_(u'Publish to')
        )
        remote_target_pages = models.CharField(max_length=2000,
            blank=True, null=True)

# endregion

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

    def get_absolute_url(self):
        target_page = self.target_page.filter(site=settings.SITE_ID).first()
        if target_page is None:
            pages = list(Page.objects.filter(application_urls='NewsApp',
                publisher_is_draft=False))
            if len(pages) == 1:
                target_page = pages[0]
            else:
                return '#'
        view_name = '%s:news-detail' % target_page.application_namespace
        return reverse(view_name, kwargs={'slug': self.slug})

    def is_remote_host(self, name):
        if name.startswith('http://'):
            return True
        if name.startswith('https://'):
            return True
        return False

    def delete(self, *args, **kwargs):
        # 2. check if this is a master
        if slumber and remote_publishing_master():
            allconf = settings.NEWS_REMOTE_PUBLISHING_CONF
            for remote_host, api_conf in allconf.iteritems():
                api_conf = settings.NEWS_REMOTE_PUBLISHING_CONF[remote_host]
                if not api_conf['remote']:
                    continue
                news_key = ':'.join([api_conf['namespace'], unicode(self.pk)])
                api = slumber.API(remote_host, auth=api_conf['auth'])
                try:
                    remote_news = api.news(news_key).get()
                    api.news(news_key).delete()
                except slumber.exceptions.HttpClientError:
                    pass

        return super(NewsItem, self).delete(*args, **kwargs)

    def serialize_target_pages(self):
        if remote_publishing_master():
            # serialize
            # self.target_page.all -> self.remote_target_pages
            try:
                self.remote_target_pages = u','.join([
                    n.application_namespace for n in self.target_page.all()
                ])
            except ValueError:
                pass

    def deserialize_target_pages(self):
        if remote_publishing_slave():
            # deserialize
            # self.remote_target_pages -> self.target_page (n:m)
            if not self.remote_target_pages is None:
                page_list = []
                for ns in self.remote_target_pages.split(','):
                    print list(Page.objects.filter(
                        publisher_is_draft=False,
                        application_namespace=ns))
                    p = Page.objects.filter(
                        publisher_is_draft=False,
                        application_namespace=ns).first()
                    if p:
                        page_list.append(p)
                self.target_page = page_list


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # 1. serialize on master side
        self.serialize_target_pages()

        # 2. save first to get PK
        result = super(NewsItem, self).save(*args, **kwargs)

        # 3. deserialize on slave side
        self.deserialize_target_pages()

        # 4. remote save()
        self.remote_save()

        return result

    def remote_save(self):
        # 4. check if this is a master -> push to slave
        if slumber and remote_publishing_master():
            from djangocms_news.serializers import NewsSerializer
            allconf = settings.NEWS_REMOTE_PUBLISHING_CONF
            for remote_host, api_conf in allconf.iteritems():
                api_conf = settings.NEWS_REMOTE_PUBLISHING_CONF[remote_host]
                if not api_conf['remote']:
                    continue
                news_key = ':'.join([api_conf['namespace'], unicode(self.pk)])
                api = slumber.API(remote_host, auth=api_conf['auth'])
                news_data = NewsSerializer(self).data
                news_data['remote_id'] = news_key
                try:
                    remote_news = api.news(news_key).get()
                    if remote_host in self.remote_publishing:
                        api.news(news_key).patch(news_data)
                        print "UPDATED"
                    else:
                        api.news(news_key).patch({'active': False})
                        print "DISABLED"
                except slumber.exceptions.HttpClientError:
                    if remote_host in self.remote_publishing:
                        api.news.post(news_data)
                        print "CREATED"


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

    news_categories = models.ManyToManyField(NewsCategory,
        blank=True,
        verbose_name=_(u'Selected news categories'))

    ordering = models.CharField(
        max_length=20,
        choices=NEWS_ORDERING_CHOICES,
        default=NEWS_ORDERING_PAST_DESC,
        verbose_name=_(u'Ordering/Selection of Articles'))

    target_page = models.ForeignKey(
        Page,
        verbose_name=_(u'Target Page'))

    def get_items(self):
        items = NewsItem.objects.filter(active=True)
        if not remote_publishing_slave():
            items = items.filter(target_page=self.target_page)
            if remote_publishing_master():
                items = items.filter(remote_publishing__icontains='localhost')

        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.ordering == self.NEWS_ORDERING_PAST_DESC:
            items = items.filter(news_date__lte=now).order_by('-news_date')
        else:
            items = items.filter(news_date__gte=now).order_by('news_date')

        print items
        return items

    def __unicode__(self):
        return self.title


class NewsImage(models.Model):
    image = ThumbnailerImageField(
        upload_to='cms_news/',
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

    news_item = models.ForeignKey(
        NewsItem,
        verbose_name=_(u'News Item'))

    if remote_publishing_slave() or remote_publishing_master():
        remote_id = models.CharField(max_length=100,
            blank=True, null=True,
            db_index=True)

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

    def delete(self, *args, **kwargs):
        # 2. check if this is a master
        if remote_publishing_master():
            allconf = settings.NEWS_REMOTE_PUBLISHING_CONF
            for remote_host, api_conf in allconf.iteritems():
                api_conf = settings.NEWS_REMOTE_PUBLISHING_CONF[remote_host]
                if not api_conf['remote']:
                    continue
                news_key = ':'.join([api_conf['namespace'], unicode(self.pk)])
                print news_key
                api = slumber.API(remote_host, auth=api_conf['auth'])
                try:
                    remote_news = api.news_image(news_key).get()
                    api.news_image(news_key).delete()
                    print "DELETED"
                except slumber.exceptions.HttpClientError:
                    print "ALREADY DELETED"

        return super(NewsImage, self).delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        # 1. save first to get PK
        result = super(NewsImage, self).save(*args, **kwargs)

        # 2. check if this is a master
        if remote_publishing_master():
            from djangocms_news.serializers import NewsImageSerializer
            allconf = settings.NEWS_REMOTE_PUBLISHING_CONF
            for remote_host, api_conf in allconf.iteritems():
                api_conf = settings.NEWS_REMOTE_PUBLISHING_CONF[remote_host]
                if not api_conf['remote']:
                    continue
                news_key = ':'.join([api_conf['namespace'], unicode(self.pk)])
                api = slumber.API(remote_host, auth=api_conf['auth'])
                news_data = NewsImageSerializer(self).data
                news_data['remote_id'] = news_key
                parent_key = ':'.join([api_conf['namespace'], unicode(self.news_item.pk)])
                print news_data
                try:
                    parent = api.news(parent_key).get()
                    parent_pk = parent['pk']
                    news_data['news_item'] = parent_pk
                except slumber.exceptions.HttpClientError:
                    continue
                try:
                    remote_news = api.news_image(news_key).get()
                    self2 = NewsImage.objects.get(pk=self.pk)
                    img_data = self2.image.read()
                    api.news_image(news_key).patch(news_data, files={
                        'image': img_data })
                    print "UPDATED"
                except slumber.exceptions.HttpClientError:
                    if remote_host in self.news_item.remote_publishing:
                        self2 = NewsImage.objects.get(pk=self.pk)
                        img_data = self2.image.read()
                        try:
                            api.news_image.post(news_data, files={
                                'image': img_data })
                        except slumber.exceptions.HttpClientError as e:
                            print e

        return result

    class Meta:
        ordering = ['ordering']
        verbose_name = _(u'News Image')
        verbose_name_plural = _(u'News Images')

if remote_publishing_master():
    from django.db.models.signals import m2m_changed

    def post_save_remote_news(sender, instance, action, reverse, *args, **kwargs):
        if action in ['post_add', 'post_delete'] and not reverse:
            instance.save()

    m2m_changed.connect(post_save_remote_news, sender=NewsItem.target_page.through)
