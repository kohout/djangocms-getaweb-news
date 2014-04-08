from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from .menu import NewsCategoryMenu

class NewsApp(CMSApp):
    name = _('News Module')
    urls = ['djangocms_news.urls']
    app_name = 'cmsnews'
    menus = [NewsCategoryMenu]

apphook_pool.register(NewsApp)
