# coding=utf-8
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.v2.serializers.wallet_serializers import UserWalletSerializer
from main.models import UserWallet, UserWalletTransaction
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class WalletViewSet(ModelViewSet):
    def create(self, request, **kwargs):
        result = {}

        wallet = UserWallet.objects.filter(user=request.user).first()

        if wallet is None:
            wallet = UserWallet()
            wallet.user = request.user
            wallet.save()

            user_wallet_trans = UserWalletTransaction()
            user_wallet_trans.wallet = wallet
            user_wallet_trans.cost = wallet.cash
            user_wallet_trans.operation = "DEPOSIT"
            user_wallet_trans.description = "مبلغ ۵۰۰ بن کوق به ارزش ۲۰۰۰ تومان شارژ گردید"
            user_wallet_trans.save()

        if wallet is not None:
            serializer = UserWalletSerializer(wallet, many=False)

            result["status"] = "OK"
            result["record"] = serializer.data
        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class WalletViewSetOAuth(ScopedProtectedResourceView, WalletViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["wallet"]


class WalletViewSetJwt(WalletViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
