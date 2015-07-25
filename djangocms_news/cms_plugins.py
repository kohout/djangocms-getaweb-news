from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import NewsTeaser
from .forms import NewsTeaserForm

class NewsTeaserPlugin(CMSPluginBase):
    model = NewsTeaser
    form = NewsTeaserForm
    name = _("News Teaser")
    render_template = "cms/plugins/news/teaser.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['items'] = instance.get_items()
        return context

plugin_pool.register_plugin(NewsTeaserPlugin)
