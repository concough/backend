from django.conf.urls import url, include

from api.v1 import views
from api.v1.views import settings_views

__author__ = 'abolfazl'

urlpatterns = (url(r'', include('api.v1.urls', namespace="default")),
               url(r'^v1/', include('api.v1.urls', namespace="v1")),
               url(r'^v2/', include('api.v2.urls', namespace="v2")),
               # url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework')),
               )
