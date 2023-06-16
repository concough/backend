"""digikunkor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from digikunkor import settings
from main.Views.index import home
from main.Views.sitemaps import StaticViewSitemap
from main.Views.static import serve_media


sitemaps = {
    'static': StaticViewSitemap(),
}

urlpatterns = []
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        url(r'^{0}(?P<path>.*)$'.format(settings.MEDIA_URL.lstrip('/')), serve_media, ),
    ]

urlpatterns += [
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'),
        name="robots"),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name="sitemap"),
    url(r'^admin/', include('admin.urls')),
    url(r'^panel/', include('dataentry.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'', include('main.urls')),
]
