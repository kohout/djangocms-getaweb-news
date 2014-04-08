from django import forms
from .models import NewsItem
from cms.models.pagemodel import Page

class NewsItemForm(forms.ModelForm):

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

