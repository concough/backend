import base64
import hashlib
import os, uuid

import rncryptor
from Crypto.Protocol import KDF
from django.shortcuts import get_object_or_404
from rest_framework import renderers
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rncryptor import RNCryptor

from digikunkor import settings
from main.models import EntranceSet, EntranceQuestionImages, Organization, Entrance, ConcoughUserPurchased
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView

__author__ = 'abolfazl'


class PNGRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class MediaEsetViewSet(APIView):
    required_scopes = ["media"]
    renderer_classes = (PNGRenderer, )

    def get(self, request, pk, **kwargs):
        # get query from db
        eset = get_object_or_404(EntranceSet, pk=pk)

        if eset.image:
            return Response(eset.image)

        raise NotFound()


class MediaEsetViewSetOauth(ScopedProtectedResourceView, MediaEsetViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["media"]


class MediaEsetViewSetJwt(MediaEsetViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class MediaOrgViewSet(APIView):
    required_scopes = ["media"]

    renderer_classes = (PNGRenderer, )

    def get(self, request, pk, **kwargs):
        # get query from db
        org = get_object_or_404(Organization, pk=pk)

        if org.image:
            return Response(org.image)

        raise NotFound()


class MediaOrgViewSetOauth(ScopedProtectedResourceView, MediaOrgViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["media"]


class MediaOrgViewSetJwt(MediaOrgViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class MyRNCryptor(rncryptor.RNCryptor):
    def _pbkdf2(self, password, salt, iterations=1023, key_length=32):
        return KDF.PBKDF2(password, salt, dkLen=key_length, count=iterations, prf=self._prf)


class MediaQuestionViewSet(APIView):
    renderer_classes = (PNGRenderer, )

    def get(self, request, uid, qid, **kwargs):
        # get query from db
        try:
            entrance = Entrance.objects.get(unique_key=uid)
            purchased = ConcoughUserPurchased.objects.get(user=request.user, entrance=entrance)

            question = get_object_or_404(EntranceQuestionImages, unique_key=qid)
            localUid = question.image.url.split('/')[3]

            username = request.user.username
            if localUid == uid:
                if question.image:
                    f = open(question.image.path, 'r')
                    data = f.read()
                    f.close()

                    hash_str = "%s:%s" % (username, settings.SECRET_KEY)
                    hash_key = hashlib.md5(hash_str).hexdigest()

                    #cryptor = rncryptor.RNCryptor()
                    cryptor = MyRNCryptor()
                    encrypted_content = cryptor.encrypt(data, hash_key)
                    b64 = base64.b64encode(encrypted_content)
                    return Response(b64)

        except:
            pass

        raise NotFound()


class MediaQuestionBulkViewSet(APIView):
    renderer_classes = (PNGRenderer, )

    def get(self, request, uid, **kwargs):
        # get query from db

        try:
            username = request.user.username
            entrance = Entrance.objects.get(unique_key=uid)
            purchased = ConcoughUserPurchased.objects.get(user=request.user, entrance=entrance)

            ids = request.GET.get("ids", "")
            if ids != "":
                ids_split = ids.split("$")
                unique_ids = [uuid.UUID(x) for x in ids_split]
                questions = EntranceQuestionImages.objects.filter(unique_key__in=unique_ids)

                result = ""
                for q in questions:
                    if q.image:
                        f = open(q.image.path, 'r')
                        data = f.read()
                        f.close()

                        hash_str = "%s:%s" % (username, settings.SECRET_KEY)
                        hash_key = hashlib.md5(hash_str).hexdigest()

                        # cryptor = rncryptor.RNCryptor()
                        cryptor = MyRNCryptor()
                        encrypted_content = cryptor.encrypt(data, hash_key)
                        b64 = base64.b64encode(encrypted_content)
                        result += q.unique_key.hex + "@" * 7 + "#" + "@" * 8 + b64 + "$" * 7 + "#" + "$" * 8

                return Response(result)

        except Exception, exc:
            print exc

        raise NotFound()



class MediaQuestionViewSetOauth(ScopedProtectedResourceView, MediaQuestionViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["media"]


class MediaQuestionViewSetJwt(MediaQuestionViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class MediaQuestionBulkViewSetOauth(ScopedProtectedResourceView, MediaQuestionBulkViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["media"]


class MediaQuestionBulkViewSetJwt(MediaQuestionBulkViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
