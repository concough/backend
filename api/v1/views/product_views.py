from datetime import datetime

import pytz
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.v1.serializers.product_serializers import EntranceSaleDataSerializer, ConcoughProductStatisticSerializer
from main.models import Entrance, EntranceSaleData, ConcoughProductStatistic
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class ProductDataViewSet(ReadOnlyModelViewSet):
    def getEntranceSale(self, request, unique_id, **kwargs):
        result = {}

        try:
            queryset = Entrance.objects.get(unique_key=unique_id)

            sale_data = EntranceSaleData.objects.filter(entrance_type=queryset.entrance_type, year=queryset.year, month=queryset.month).first()
            serializer3 = EntranceSaleDataSerializer(sale_data, many=False)

            if sale_data:
                result["status"] = "OK"
                result["sale_data"] = {"sale_record": serializer3.data,
                                       "discount": 0}
            else:
                result["status"] = "Error"
                result["error_type"] = "EmptyArray"

        except Entrance.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"

        return Response(result)

    def getEntranceStat(self, request, unique_id, **kwargs):
        result = {}

        try:
            queryset = Entrance.objects.get(unique_key=unique_id)

            stat_record = ConcoughProductStatistic.objects.filter(entrance__id=queryset.id).first()
            serializer4 = ConcoughProductStatisticSerializer(stat_record, many=False)

            d = serializer4.data
            date = datetime.now(tz=pytz.UTC)

            delta = date - queryset.last_published
            # d["purchased"] += 500 + (date.timetuple().tm_yday * 3) + d["purchased"]
            if delta.days <= 10:
                d["purchased"] += ((3100 - (queryset.id * 3)) * 2) + (date.timetuple().tm_yday * 2) + d["purchased"] - ((10 - delta.days) * 100)
            else:
                d["purchased"] += ((3100 - (queryset.id * 3)) * 2) + (date.timetuple().tm_yday * 2) + d["purchased"]

            if stat_record:
                result["status"] = "OK"
                result["stat_data"] = d
            else:
                result["status"] = "Error"
                result["error_type"] = "EmptyArray"

        except Entrance.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"

        return Response(result)


class ProductDataViewSetOAuth(ScopedProtectedResourceView, ProductDataViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["product"]


class ProductDataViewSetJwt(ProductDataViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)