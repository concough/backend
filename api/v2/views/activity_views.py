# Create your views here.
from django.utils.datetime_safe import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.v2.serializers.activity_serializers import ActivitySerializer
from main.Helpers.model_static_values import CONCOUGH_LOG_TYPES, CONCOUGH_LOG_TYPES_2
from main.models import ConcoughActivity
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


# class JSONResponse(HttpResponse):
#     """
#     An HttpResponse that renders its content into JSON
#     """
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JSONResponse, self).__init__(content, **kwargs)


class ActivityViewSet(ReadOnlyModelViewSet):
    def list(self, request, **kwargs):
        queryset = ConcoughActivity.objects.filter(activity_type__in=CONCOUGH_LOG_TYPES_2).prefetch_related('target')[:10]
        serializer = ActivitySerializer(queryset, many=True)
        #return Response([])
        return Response(serializer.data)

    # def updates(self, request, last, **kwargs):
    #     d = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")
    #
    #     queryset = ConcoughActivity.objects.filter(created__gt=d).prefetch_related('target')
    #     serializer = ActivitySerializer(queryset, many=True)
    #     return Response(serializer.data)

    def next_page(self, request, last, **kwargs):
        try:
            d = datetime.strptime(last, "%Y-%m-%dT%H:%M:%S.%fZ")

            queryset = ConcoughActivity.objects.filter(activity_type__in=CONCOUGH_LOG_TYPES_2, created__lt=d).prefetch_related('target')[:10]
            serializer = ActivitySerializer(queryset, many=True)

            return Response(serializer.data)

        except:
            return []


class ActivityViewSetOauth(ScopedProtectedResourceView, ActivityViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated, )

    required_scopes = ["activities"]


class ActivityViewSetJwt(ActivityViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
