from datetime import datetime

import pytz
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.v2.serializers.purchase_serializers import ConcoughUserPurchasedSerializer, ConcoughUserPurchasedFullSerializer
from main.models import ConcoughUserPurchased, Entrance, ConcoughProductStatistic, EntranceLessonTagPackage
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class UserPurchaseViewSet(ReadOnlyModelViewSet):
    def getEntrance(self, request, unique_id, **kwargs):
        result = {}

        try:
            queryset = Entrance.objects.get(unique_key=unique_id)
            user = request.user

            # loads purchased status
            purchase_query = ConcoughUserPurchased.objects.filter(entrance=queryset, user=user).first()
            serializer2 = ConcoughUserPurchasedSerializer(purchase_query, many=False)

            if purchase_query:
                result["purchase"] = {"status": True,
                                      "purchase_record": serializer2.data
                                      }

            else:
                result["purchase"] = {"status": False}

            result["status"] = "OK"

        except Entrance.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"

        return Response(result)

    def getEntranceLessonTags(self, request, unique_id, **kwargs):
        result = {}

        try:
            queryset = EntranceLessonTagPackage.objects.get(unique_key=unique_id)
            user = request.user

            # loads purchased status
            purchase_query = ConcoughUserPurchased.objects.filter(entrance_tags=queryset, user=user).first()
            serializer2 = ConcoughUserPurchasedSerializer(purchase_query, many=False)

            if purchase_query:
                result["purchase"] = {"status": True,
                                      "purchase_record": serializer2.data
                                      }

            else:
                result["purchase"] = {"status": False}

            result["status"] = "OK"

        except EntranceLessonTagPackage.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceTagsNotExist"

        return Response(result)

    def getAllPurhases(self, request, **kwargs):
        result = {}

        user = request.user
        purchase_query = ConcoughUserPurchased.objects.filter(user=user)

        if len(purchase_query):
            serializer2 = ConcoughUserPurchasedFullSerializer(purchase_query, many=True)

            result["status"] = "OK"
            result["records"] = serializer2.data
        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)

    def putDownloadPlus(self, request, unique_id, **kwargs):
        result = {}

        user = request.user
        try:
            queryset = Entrance.objects.get(unique_key=unique_id)

            # loads purchased status
            purchase_query = ConcoughUserPurchased.objects.filter(entrance=queryset,
                                                                  user=user).first()

            serializer2 = ConcoughUserPurchasedSerializer(purchase_query, many=False)

            result["purchase"] = {"status": True,
                                  "purchase_record": serializer2.data
                                  }

            if purchase_query:
                if purchase_query.downloaded != 0:
                    diff_seconds = (datetime.now(tz=pytz.UTC) - purchase_query.updated).seconds
                    if diff_seconds >= 300:
                        with transaction.atomic():
                            purchase_query.downloaded += 1
                            purchase_query.save()

                            stats = ConcoughProductStatistic.objects.filter(entrance=queryset).first()
                            if stats:
                                stats.downloaded += 1
                                stats.save()
                else:
                    with transaction.atomic():
                        purchase_query.downloaded += 1
                        purchase_query.save()

                        stats = ConcoughProductStatistic.objects.filter(entrance=queryset).first()
                        if stats:
                            stats.downloaded += 1
                            stats.save()

                serializer2 = ConcoughUserPurchasedSerializer(purchase_query, many=False)

                result["purchase"] = {"status": True,
                                      "purchase_record": serializer2.data
                                      }

            else:
                result["purchase"] = {"status": False}

            result["status"] = "OK"

        except Entrance.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"

        return Response(result)


class UserPurchaseViewSetOAuth(ScopedProtectedResourceView, UserPurchaseViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["purchase"]


class UserPurchaseViewSetJwt(UserPurchaseViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)