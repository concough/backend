from django.contrib import sitemaps
from django.core.urlresolvers import reverse

__author__ = 'abolfazl'


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    #i18n = True

    def items(self):
        return ['main.home', 'main.auth.login']

    def location(self, item):
        return reverse(item)
