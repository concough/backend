import hashlib

from Crypto.Protocol import KDF
from django.db.models.aggregates import Count, Sum
import base64
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.v1.serializers.entrance_serializers import EntranceSerializer
from digikunkor import settings
from main.models import Entrance, EntrancePackage, EntrancePackageType, ConcoughUserPurchased

from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView

import rncryptor

class MyRNCryptor(rncryptor.RNCryptor):
    def _pbkdf2(self, password, salt, iterations=1023, key_length=32):
        return KDF.PBKDF2(password, salt, dkLen=key_length, count=iterations, prf=self._prf)


class EntranceViewSet(ReadOnlyModelViewSet):
    def get(self, request, unique_id, **kwargs):
        result = {}

        try:
            queryset = Entrance.objects.annotate(booklets_count=Count('booklets'), duration=Sum('booklets__duration'))\
                .get(unique_key=unique_id)
            serializer = EntranceSerializer(queryset, many=False)

            if queryset:
                # profile data exist
                result["status"] = "OK"
                result["records"] = serializer.data

            else:
                result["status"] = "Error"
                result["error_type"] = "EmptyArray"

        except Entrance.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"
        except Exception:
            result["status"] = "Error"
            result["error_type"] = "RemoteDBError"

        return Response(result)

    def getPackageInit(self, request, unique_id, **kwargs):
        result = {}

        username = request.user.username

        try:
            entrance = Entrance.objects.get(unique_key=unique_id, published=True)
            purchase_record = ConcoughUserPurchased.objects.filter(entrance=entrance,
                                                                   user__id=request.user.id).first()

            if purchase_record:
                entrance_package_type = EntrancePackageType.objects.get(title="CREATE")
                entrance_package = EntrancePackage.objects.filter(entrance=entrance,
                                                                  package_type=entrance_package_type).first()

                if entrance_package:
                    hash_str = "%s:%s" % (username, settings.SECRET_KEY)
                    hash_key = str(hashlib.md5(hash_str).hexdigest())

                    cryptor = MyRNCryptor()
                    encrypted_content = cryptor.encrypt(entrance_package.content, hash_key)

                    print hash_str, hash_key

                    result["status"] = "OK"
                    result["package"] = base64.b64encode(encrypted_content)
                else:
                    result["status"] = "Error"
                    result["error_type"] = "PackageNotExist"

            else:
                result["status"] = "Error"
                result["error_type"] = "EntranceNotPurchased"

        except Entrance.DoesNotExist, exc:
            print exc
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"
        except Exception, exc:
            print exc
            result["status"] = "Error"
            result["error_type"] = "RemoteDBError"

        return Response(result)


class EntranceViewSetOAuth(ScopedProtectedResourceView, EntranceViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["entrance"]


class EntranceViewSetJwt(EntranceViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)