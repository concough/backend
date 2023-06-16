# coding=utf-8
from datetime import datetime

import pytz
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from uuid import UUID

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet

from api.v2.serializers.entrance_tags_serializers import EntranceTagPackageSerializer
from api.v2.serializers.product_serializers import EntranceSaleDataSerializer, ConcoughProductStatisticSerializer, \
    EntranceTagsSaleDataSerializer
from main.models import Entrance, ConcoughUserPurchased, UserWallet, UserWalletTransaction, EntranceSaleData, \
    ConcoughProductStatistic, EntranceMulti, EntranceBookletDetail, EntranceLessonTagPackage, EntranceTagSaleData
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


class ProductDataExtraViewSet(ProductDataViewSet):
    def getEntranceMultiSale(self, request, unique_id, **kwargs):
        result = {}
        try:
            queryset = EntranceMulti.objects.prefetch_related('entrances').get(unique_key=unique_id)

            entrances = queryset.entrances.all()
            sale_data = EntranceSaleData.objects.filter(entrance_type=entrances[0].entrance_type)

            sale_data_array = {}
            total_cost = 0
            cost = 0
            for sale in sale_data:
                sale_data_array["%s-%s" % (sale.year, sale.month)] = sale.cost_bon

            # ids = []
            # for ent in entrances:
            #     ids.append(ent.id)

            purchased = ConcoughUserPurchased.objects.filter(user=request.user, entrance__in=entrances)
            purchased_ids = []
            for pur in purchased:
                purchased_ids.append(pur.target_id)

            for ent in entrances:
                key = "%s-%s" % (ent.year, ent.month)
                if key in sale_data_array:
                    total_cost += sale_data_array[key]

                    if ent.id not in purchased_ids:
                        cost += sale_data_array[key]

            if sale_data:
                result["status"] = "OK"
                result["sale_data"] = {"sale_record": {
                    "total_cost": total_cost,
                    "cost": cost
                },
                                       "discount": 0}
            else:
                result["status"] = "Error"
                result["error_type"] = "EmptyArray"

        except EntranceMulti.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "NotExist"

        return Response(result)

    def getEntranceSaleAndStat(self, request, unique_id, **kwargs):
        result = {}

        try:
            queryset = Entrance.objects.get(unique_key=unique_id)

            sale_data = EntranceSaleData.objects.filter(entrance_type=queryset.entrance_type, year=queryset.year,
                                                        month=queryset.month).first()
            serializer3 = EntranceSaleDataSerializer(sale_data, many=False)

            stat_record = ConcoughProductStatistic.objects.filter(entrance__id=queryset.id).first()
            serializer4 = ConcoughProductStatisticSerializer(stat_record, many=False)

            d = serializer4.data
            date = datetime.now(tz=pytz.UTC)

            delta = date - queryset.last_published
            # d["purchased"] += 500 + (date.timetuple().tm_yday * 3) + d["purchased"]
            if delta.days <= 10:
                d["purchased"] += ((3100 - (queryset.id * 3)) * 2) + (date.timetuple().tm_yday * 2) + d["purchased"] - (
                (10 - delta.days) * 100)
            else:
                d["purchased"] += ((3100 - (queryset.id * 3)) * 2) + (date.timetuple().tm_yday * 2) + d["purchased"]

            result["status"] = "OK"
            if stat_record:
                result["stat_data"] = d
            else:
                result["stat_data"] = None

            if sale_data:
                result["sale_data"] = {"sale_record": serializer3.data,
                                       "discount": 0}
            else:
                result["sale_data"] = None

        except Entrance.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceNotExist"

        return Response(result)

    def getEntranceTagsData(self, request, unique_id, bid, **kwargs):
        result = {}

        try:
            booklet_detail = EntranceBookletDetail.objects.prefetch_related('booklet', 'booklet__entrance',
                                                                            'booklet__entrance__entrance_type').get(pk=bid)
            if booklet_detail.booklet.entrance.unique_key == UUID(unique_id):

                package = EntranceLessonTagPackage.objects.get(booklet_detail=booklet_detail)

                sale_data = EntranceTagSaleData.objects.filter(entrance_type=booklet_detail.booklet.entrance.entrance_type,
                                                            year=booklet_detail.booklet.entrance.year,
                                                            month=booklet_detail.booklet.entrance.month).first()
                stat_record = ConcoughProductStatistic.objects.filter(entrance_tags__booklet_detail=booklet_detail).first()

                serializer = EntranceTagPackageSerializer(package, many=False)
                serializer3 = EntranceTagsSaleDataSerializer(sale_data, many=False)
                serializer4 = ConcoughProductStatisticSerializer(stat_record, many=False)

                result["status"] = "OK"
                result["record"] = serializer.data

                if stat_record:
                    result["stat_data"] = serializer4.data
                else:
                    result["stat_data"] = None

                if sale_data:
                    result["sale_data"] = {"sale_record": serializer3.data,
                                           "discount": 0}
                else:
                    result["sale_data"] = None

        except EntranceBookletDetail.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceBookletDetailNotExist"

        except EntranceLessonTagPackage.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EntranceTagsNotExist"

        return Response(result)


class ProductDataViewSetOAuth(ScopedProtectedResourceView, ProductDataExtraViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["product"]


class ProductDataViewSetJwt(ProductDataExtraViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class ProductPurchaseViewSet(ViewSet):
    def addToLibrary(self, request, **kwargs):
        result = {}

        product_id = request.data.get("product_id", "").strip()
        product_type = request.data.get("product_type", "").strip()

        if product_id != "" and product_type != "":
            try:
                if product_type == "Entrance":
                    puid = UUID(product_id)
                    entrance = Entrance.objects.get(unique_key=puid)
                    ctype = ContentType.objects.get_for_model(Entrance)

                    purchased = ConcoughUserPurchased.objects.filter(target_ct=ctype, target_id=entrance.id,
                                                                     user=request.user)

                    if len(purchased) > 0:
                        result["status"] = "Error"
                        result["error_type"] = "DuplicateSale"
                        result["purchased"] = []
                        result["purchased"].append({
                            "purchase_id": purchased[0].id,
                            "purchase_time": purchased[0].created,
                            "downloaded": purchased[0].downloaded,
                        })

                    else:
                        entrance_sale = EntranceSaleData.objects.get(entrance_type__id=entrance.entrance_type.id,
                                                                     year=entrance.year,
                                                                     month=entrance.month)

                        wallet = UserWallet.objects.filter(user=request.user).first()
                        can_purchase = True

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
                        else:
                            if entrance_sale.cost_bon > wallet.cash:
                                can_purchase = False

                        if can_purchase:
                            # update product statistics
                            result["purchased"] = []

                            with transaction.atomic():
                                purchase = ConcoughUserPurchased()
                                purchase.target = entrance
                                purchase.user = request.user
                                purchase.payed_amount = entrance_sale.cost_bon
                                purchase.save()

                                stat_record = ConcoughProductStatistic.objects.get(entrance=entrance)
                                stat_record.purchased += 1
                                stat_record.save()

                                if entrance_sale.cost_bon > 0:
                                    wallet.cash = wallet.cash - entrance_sale.cost_bon
                                    wallet.save()

                                    user_wallet_trans = UserWalletTransaction()
                                    user_wallet_trans.wallet = wallet
                                    user_wallet_trans.cost = wallet.cash
                                    user_wallet_trans.operation = "REMOVAL"
                                    user_wallet_trans.description = "مبلغ %s بابت خرید آزمون کسر گردید" % entrance_sale.cost_bon
                                    user_wallet_trans.save()

                            result["purchased"].append({
                                "purchase_id": purchase.id,
                                "purchase_time": purchase.created,
                                "downloaded": purchase.downloaded,
                            })
                            result["wallet_cash"] = wallet.cash
                            result["wallet_updated"] = wallet.updated
                            result["status"] = "OK"

                        else:
                            result["status"] = "Error"
                            result["error_type"] = "WalletNotEnoughCash"

                elif product_type == "EntranceMulti":
                    puid = UUID(product_id)
                    emulti = EntranceMulti.objects.get(unique_key=puid)

                    wallet = UserWallet.objects.filter(user=request.user).first()
                    can_purchase = True

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

                    entrances = emulti.entrances.all()
                    ctype = ContentType.objects.get_for_model(Entrance)

                    entrances_dict = {}
                    for entrance in entrances:
                        entrances_dict[entrance.id] = entrance

                    purchased = ConcoughUserPurchased.objects.filter(target_ct=ctype, target_id__in=entrances_dict.keys(),
                                                                     user=request.user)

                    for p in purchased:
                        del entrances_dict[p.target_id]

                    if len(entrances_dict) > 0:
                        total_cost_bon = 0
                        sale_info_dict = {}
                        for ent in entrances_dict.values():
                            entrance_sale = EntranceSaleData.objects.get(entrance_type__id=ent.entrance_type.id,
                                                                         year=ent.year,
                                                                         month=ent.month)
                            sale_info_dict[ent.unique_key.get_hex] = entrance_sale
                            total_cost_bon += entrance_sale.cost_bon

                        if total_cost_bon > wallet.cash:
                            can_purchase = False

                        if can_purchase:
                            result["purchased"] = []
                            for ent in entrances_dict.values():
                                with transaction.atomic():
                                    purchase = ConcoughUserPurchased()
                                    purchase.target = ent
                                    purchase.user = request.user
                                    purchase.payed_amount = sale_info_dict[ent.unique_key.get_hex].cost_bon
                                    purchase.save()

                                    stat_record = ConcoughProductStatistic.objects.get(entrance=ent)
                                    stat_record.purchased += 1
                                    stat_record.save()

                                    if sale_info_dict[ent.unique_key.get_hex].cost_bon > 0:
                                        print entrance_sale.cost_bon
                                        wallet.cash = wallet.cash - sale_info_dict[ent.unique_key.get_hex].cost_bon
                                        wallet.save()
                                        print(wallet.cash)

                                        user_wallet_trans = UserWalletTransaction()
                                        user_wallet_trans.wallet = wallet
                                        user_wallet_trans.cost = wallet.cash
                                        user_wallet_trans.operation = "REMOVAL"
                                        user_wallet_trans.description = "مبلغ %s بابت خرید آزمون کسر گردید" % entrance_sale.cost_bon
                                        user_wallet_trans.save()

                                    result["purchased"].append({
                                        "purchase_id": purchase.id,
                                        "purchase_time": purchase.created,
                                        "downloaded": purchase.downloaded,
                                        "product_key": ent.unique_key.get_hex()
                                    })

                            result["wallet_cash"] = wallet.cash
                            result["wallet_updated"] = wallet.updated
                            result["status"] = "OK"

                        else:
                            result["status"] = "Error"
                            result["error_type"] = "WalletNotEnoughCash"

                    else:
                        result["status"] = "Error"
                        result["error_type"] = "UnsupportedVersion"

                elif product_type == "EntranceTags":
                    puid = UUID(product_id)
                    entrance_tag_package = EntranceLessonTagPackage.objects.prefetch_related("booklet_detail__booklet__entrance").get(unique_key=puid)
                    ctype = ContentType.objects.get_for_model(EntranceLessonTagPackage)

                    purchased = ConcoughUserPurchased.objects.filter(target_ct=ctype, target_id=entrance_tag_package.id,
                                                                     user=request.user)

                    if len(purchased) > 0:
                        result["status"] = "Error"
                        result["error_type"] = "DuplicateSale"
                        result["purchased"] = []
                        result["purchased"].append({
                            "purchase_id": purchased[0].id,
                            "purchase_time": purchased[0].created,
                            "downloaded": purchased[0].downloaded,
                        })

                    else:
                        entrance_tag_package_sale = EntranceTagSaleData.objects.get(entrance_type__id=entrance_tag_package.entrance_type.id,
                                                                     year=entrance_tag_package.booklet_detail.booklet.entrance.year,
                                                                     month=entrance_tag_package.booklet_detail.booklet.entrance.month)

                        wallet = UserWallet.objects.filter(user=request.user).first()
                        can_purchase = True

                        final_cost = int((float(entrance_tag_package.q_count) / float(entrance_tag_package_sale.q_count)) * entrance_tag_package_sale.cost)

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
                        else:
                            if final_cost > wallet.cash:
                                can_purchase = False

                        if can_purchase:
                            # update product statistics
                            result["purchased"] = []

                            with transaction.atomic():
                                purchase = ConcoughUserPurchased()
                                purchase.target = entrance_tag_package
                                purchase.user = request.user
                                purchase.payed_amount = entrance_tag_package_sale.cost
                                purchase.save()

                                stat_record = ConcoughProductStatistic.objects.get(entrance_tags=entrance_tag_package)
                                stat_record.purchased += 1
                                stat_record.save()

                                if final_cost > 0:
                                    wallet.cash = wallet.cash - final_cost
                                    wallet.save()

                                    user_wallet_trans = UserWalletTransaction()
                                    user_wallet_trans.wallet = wallet
                                    user_wallet_trans.cost = wallet.cash
                                    user_wallet_trans.operation = "REMOVAL"
                                    user_wallet_trans.description = "مبلغ %s بابت خرید آزمون کسر گردید" % entrance_tag_package_sale.cost
                                    user_wallet_trans.save()

                            result["purchased"].append({
                                "purchase_id": purchase.id,
                                "purchase_time": purchase.created,
                                "downloaded": purchase.downloaded,
                            })
                            result["wallet_cash"] = wallet.cash
                            result["wallet_updated"] = wallet.updated
                            result["status"] = "OK"

                        else:
                            result["status"] = "Error"
                            result["error_type"] = "WalletNotEnoughCash"

            except MultipleObjectsReturned:
                result["status"] = "Error"
                result["error_type"] = "DuplicateSale"

            except Entrance.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "ProductNotExist"

            except EntranceMulti.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "ProductNotExist"

            except IntegrityError:
                result["status"] = "Error"
                result["error_type"] = "DuplicateSale"

            except Exception:
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


class ProductPurchaseViewSetOAuth(ScopedProtectedResourceView, ProductPurchaseViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["product"]


class ProductPurchaseViewSetJwt(ProductPurchaseViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)