from digikunkor import settings

__author__ = 'abolfazl'

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse


class BuildAbsoluteURIMixin(object):
    protocol = 'http'

    def get_domain(self):
        return Site.objects.get_current().domain

    def get_protocol(self):
        if settings.DEV_ENVIRONMENT == "deplpy":
            return "%ss" % self.protocol

        return self.protocol

    def reverse_absolute_uri(self, view_name, *args, **kwargs):
        location = reverse(view_name, args=args, kwargs=kwargs)
        return self.build_absolute_uri(location)

    def build_absolute_uri(self, location):
        return '{protocol}://{domain}{location}'.format(
            protocol=self.get_protocol(),
            domain=self.get_domain(),
            location=location,
        )
