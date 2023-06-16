from django.db.models import Count, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.v1.serializers.archive_serializers import ArchiveEntranceSetSerializer, ArchiveEntranceSerializer
from api.v1.serializers.general_serializers import EntranceTypeWithIdSerializer, EntranceSetSerializer, \
    ExaminationGroupSerializer, ExaminationGroupWithIdSerializer
from main.models import EntranceType, EntranceSet, ExaminationGroup, Entrance
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class EntranceTypeViewSet(ReadOnlyModelViewSet):
    def list(self, request, **kwargs):
        queryset = EntranceType.objects.values('id', 'title')
        serializer = EntranceTypeWithIdSerializer(queryset, many=True)

        result = {}
        if len(queryset) > 0:
            # profile data exist
            result["status"] = "OK"
            result["record"] = serializer.data

        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class EntranceTypeViewSetOAuth(ScopedProtectedResourceView, EntranceTypeViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["archive"]


class EntranceTypeViewSetJwt(EntranceTypeViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class ExaminationGroupViewSet(ReadOnlyModelViewSet):
    def list(self, request, etype, **kwargs):
        queryset = ExaminationGroup.objects.all().filter(etype__id=etype)
        serializer = ExaminationGroupWithIdSerializer(queryset, many=True)

        result = {}
        if len(queryset) > 0:
            # profile data exist
            result["status"] = "OK"
            result["record"] = serializer.data

        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class ExaminationGroupViewSetOAuth(ScopedProtectedResourceView, ExaminationGroupViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["archive"]


class ExaminationGroupViewSetJwt(ExaminationGroupViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class EntranceSetViewSet(ReadOnlyModelViewSet):
    def list(self, request, egroup, **kwargs):
        queryset = EntranceSet.objects.filter(group__id=egroup, entrances__published=True)\
            .annotate(entrance_count=Count('entrances'))

        serializer = ArchiveEntranceSetSerializer(queryset, many=True)

        result = {}
        if len(queryset) > 0:
            # profile data exist
            result["status"] = "OK"
            result["record"] = serializer.data

        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class EntranceSetViewSetOAuth(ScopedProtectedResourceView, EntranceSetViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["archive"]


class EntranceSetViewSetJwt(EntranceSetViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class EntrancesViewSet(ReadOnlyModelViewSet):
    def list(self, request, eset, **kwargs):
        queryset = Entrance.objects.annotate(booklets_count=Count('booklets'), duration=Sum('booklets__duration'))\
            .filter(entrance_set__id=eset, published=True)\
            .prefetch_related('organization').order_by('-year', '-month')
        serializer = ArchiveEntranceSerializer(queryset, many=True)

        result = {}
        if len(queryset) > 0:
            # profile data exist
            result["status"] = "OK"
            result["record"] = serializer.data

        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class EntrancesViewSetOAuth(ScopedProtectedResourceView, EntrancesViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["archive"]


class EntrancesViewSetJwt(EntrancesViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
