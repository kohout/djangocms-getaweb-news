# -*- coding: utf-8 -*-
from django import forms
from .fields import MultiSelectFormField
from .models import NewsTeaser, NewsItem, remote_publishing_master
from cms.models.pagemodel import Page
from django.conf import settings
from multiupload.fields import MultiFileField

class UploadForm(forms.ModelForm):
    attachments = MultiFileField(min_num=1, max_num=15,
        label=u'Dateien auswählen',
        max_file_size=1024*1024*5)
    class Meta:
        model = NewsItem
        fields = ('attachments', )

class TextCheckboxSelectMultiple(forms.widgets.CheckboxSelectMultiple):
    """
    Set checked values based on a comma separated list instead of a python list
    """
    def render(self, name, value, **kwargs):
        if isinstance(value, basestring):
            value = value.split(u",")
        return super(TextCheckboxSelectMultiple, self).render(name, value, **kwargs)


class TextMultiField(forms.MultipleChoiceField):
    """
    Work in conjunction with TextCheckboxSelectMultiple to store a
    comma separated list of multiple choice values in a CharField/TextField
    """
    widget = TextCheckboxSelectMultiple

    def validate(self, value):
        pass

    def clean(self, value):
        val = super(TextMultiField, self).clean(value)
        return u",".join(val)


class NewsTeaserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NewsTeaserForm, self).__init__(*args, **kwargs)
        self.fields['target_page'].queryset = Page.objects.filter(
            publisher_is_draft=True)

    class Meta:
        model = NewsTeaser
        fields = (
            'title',
            'news_categories',
            'target_page',
            'ordering',
        )


class NewsItemForm(forms.ModelForm):

    if remote_publishing_master():
        remote_publishing = MultiSelectFormField(
            choices=settings.NEWS_REMOTE_PUBLISHING_CHOICES)

    def label_from_instance(self, obj):
        """
        custom label method that is replaced in the ModelChoiceField
        """
        return obj.get_page_title()

    def __init__(self, *args, **kwargs):
        super(NewsItemForm, self).__init__(*args, **kwargs)
        self.fields['target_page'].label_from_instance = \
            self.label_from_instance

        self.fields['target_page'].queryset = Page.objects.filter(
            application_urls='NewsApp', publisher_is_draft=False)

    class Meta:
        model = NewsItem
        fields = (
            'active',
            'news_date',
            'title',
            'abstract',
            'content',
            'tags',
            'news_categories',
            'target_page',
            'price',
            'youtube_id',
            'additional_images_pagination',
            'additional_images_speed',
        )
