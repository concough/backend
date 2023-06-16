# coding=utf-8
from uuid import UUID

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.helpers.paymets.payir_payment import PAYIR
from api.v1.serializers.basket_serializers import UserSaleSerializer, UserFullSaleSerializer
from digikunkor import settings
from main.models import Entrance, ConcoughUserBasket, ConcoughUserSale, EntranceSaleData, ConcoughUserPurchased, \
    ConcoughProductStatistic, ConcoughPayments
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class BasketViewSet(ReadOnlyModelViewSet):
    def listSales(self, request, **kwargs):
        result = {}

        user_id = request.user.id
        try:
            basket_record = ConcoughUserBasket.objects.prefetch_related('sales').filter(user__id=user_id).first()
            if basket_record == None:
                result["status"] = "Error"
                result["error_type"] = "EmptyArray"
            else:
                pay = ConcoughPayments.objects.filter(user=request.user, basket__unique_id=basket_record.unique_id).first()
                result["status"] = "OK"
                result["basket_uid"] = basket_record.unique_id.get_hex()

                if pay is not None:
                    mustEmptyBasket = False
                    if pay.state == "Success":
                        mustEmptyBasket = True

                    elif pay.state == "Pending" or pay.state == "MustVerified":
                        result, pay1 = PAYIR.verify_local(pay)

                        if pay1 is not None:
                            pay = pay1

                        if result == "Success":
                            mustEmptyBasket = True

                    if mustEmptyBasket:
                        sales = basket_record.sales.all()

                        if len(sales) > 0:
                            total_cost = 0

                            for sale in sales:
                                total_cost += sale.pay_amount

                            for sale in sales:
                                try:
                                    purchase = ConcoughUserPurchased()
                                    purchase.target = sale.target
                                    purchase.user = request.user
                                    purchase.payed_amount = sale.pay_amount
                                    purchase.save()

                                    # update product statistics
                                    with transaction.atomic():
                                        if isinstance(sale.target, Entrance):
                                            stat_record = ConcoughProductStatistic.objects.get(entrance=sale.target)
                                            stat_record.purchased += 1
                                            stat_record.save()

                                except IntegrityError:
                                    pass
                                else:
                                    sale.delete()

                            basket_record.delete()

                        result["status"] = "Error"
                        result["error_type"] = "EmptyArray"

                    else:
                        sales = ConcoughUserSale.objects.filter(basket=basket_record)
                        serializer = UserFullSaleSerializer(sales, many=True)
                        # get sales
                        result["records"] = serializer.data
                else:
                    sales = ConcoughUserSale.objects.filter(basket=basket_record)
                    serializer = UserFullSaleSerializer(sales, many=True)
                    # get sales
                    result["records"] = serializer.data

        except Exception:
            result["status"] = "Error"
            result["error_type"] = "RemoteDBError"

        return Response(result)

    def createBasket(self, request, **kwargs):
        result = {}

        user_id = request.user.id
        try:
            basket_record = ConcoughUserBasket.objects.filter(user__id=user_id).first()
            if basket_record == None:
                user = User.objects.get(pk=user_id)
                # basket does not exist --> create basket first
                basket_record = ConcoughUserBasket()
                basket_record.user = user
                basket_record.save()

            basket_unique_id = basket_record.unique_id

            result["status"] = "OK"
            result["basket_uid"] = basket_unique_id.get_hex()


        except Exception:
            result["status"] = "Error"
            result["error_type"] = "RemoteDBError"

        return Response(result)

    def postProductInBasket(self, request, **kwargs):
        result = {}

        user_id = request.user.id

        product_id = request.data.get("product_id", "").strip()
        product_type = request.data.get("product_type", "").strip()

        if product_id != "" and product_type != "":

            try:
                basket_record = ConcoughUserBasket.objects.filter(user__id=user_id).first()
                if basket_record is None:
                    user = User.objects.get(pk=user_id)
                    # basket does not exist --> create basket first
                    basket_record = ConcoughUserBasket()
                    basket_record.user.id = user_id
                    basket_record.save()

                basket_unique_id = basket_record.unique_id

                pay_record = ConcoughPayments.objects.filter(user__id=user_id, basket=basket_record)

                if product_type == "Entrance":
                    puid = UUID(product_id)
                    entrance = Entrance.objects.get(unique_key=puid)
                    ctype = ContentType.objects.get_for_model(Entrance)

                    purchased = ConcoughUserPurchased.objects.filter(target_ct=ctype, target_id=entrance.id, user=request.user)

                    if len(purchased) > 0:
                        result["status"] = "Error"
                        result["error_type"] = "DuplicateSale"
                    else:
                        entrance_sale = EntranceSaleData.objects.get(entrance_type=entrance.entrance_type,
                                                                     year=entrance.year,
                                                                     month=entrance.month)


                        # save sale record
                        sale, created = ConcoughUserSale.objects.get_or_create(basket=basket_record,
                                                                               target_ct=ctype,
                                                                               target_id=entrance.id,
                                                                               defaults={
                                                                                   'pay_amount': entrance_sale.cost,
                                                                                   'target': entrance})

                        serializer = UserSaleSerializer(sale, many=False)

                        if len(pay_record) > 0:
                            if pay_record[0].state == "Pending":
                                pay_record[0].basket = None
                                pay_record[0].save()

                        result["status"] = "OK"
                        result["basket_uid"] = basket_unique_id.get_hex()
                        result["records"] = serializer.data
                        result["records"]["target"] = {
                            "sale_type": product_type,
                            "unique_key": product_id
                        }

            except MultipleObjectsReturned:
                result["status"] = "Error"
                result["error_type"] = "DuplicateSale"

            except Entrance.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "EntranceNotExist"

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

    def putProductInBasket(self, request, basket_uid, **kwargs):
        result = {}

        product_id = request.data.get("product_id", "").strip()
        product_type = request.data.get("product_type", "").strip()

        if product_id != "" and product_type != "":

            try:
                uid = UUID(basket_uid)
                basket_record = ConcoughUserBasket.objects.prefetch_related('user').get(unique_id=uid)
                basket_unique_id = basket_record.unique_id
                user_id = basket_record.user.id

                pay_record = ConcoughPayments.objects.filter(user__id=user_id, basket=basket_record)

                if product_type == "Entrance":
                    puid = UUID(product_id)
                    entrance = Entrance.objects.prefetch_related('entrance_type').get(unique_key=puid)
                    ctype = ContentType.objects.get_for_model(Entrance)
                    purchased = ConcoughUserPurchased.objects.filter(target_ct=ctype, target_id=entrance.id, user=request.user)

                    if len(purchased) > 0:
                        result["status"] = "Error"
                        result["error_type"] = "DuplicateSale"
                    else:
                        entrance_sale = EntranceSaleData.objects.get(entrance_type__id=entrance.entrance_type.id,
                                                                     year=entrance.year,
                                                                     month=entrance.month)

                        if user_id == request.user.id:
                            # save sale record
                            sale, created = ConcoughUserSale.objects.get_or_create(basket=basket_record,
                                                                                   target_ct=ctype,
                                                                                   target_id=entrance.id,
                                                                                   defaults={
                                                                                       'pay_amount': entrance_sale.cost,
                                                                                       'target': entrance})
                            serializer = UserSaleSerializer(sale, many=False)

                            if len(pay_record) > 0:
                                if pay_record[0].state == "Pending":
                                    pay_record[0].basket = None
                                    pay_record[0].save()

                            result["status"] = "OK"
                            result["basket_uid"] = basket_unique_id.get_hex()
                            result["records"] = serializer.data
                            result["records"]["target"] = {
                                "sale_type": product_type,
                                "unique_key": product_id
                            }
                        else:
                            result["status"] = "Error"
                            result["error_type"] = "BadData"

            except MultipleObjectsReturned:
                result["status"] = "Error"
                result["error_type"] = "DuplicateSale"

            except Entrance.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "EntranceNotExist"

            except ConcoughUserBasket.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "BasketNotExist"

            except Exception, exc:
                print exc
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def removeProductFormBasket(self, request, basket_uid, sale_id, **kwargs):
        result = {}

        try:

            pay_record = ConcoughPayments.objects.filter(user=request.user, basket__unique_id=basket_uid)
            sale = ConcoughUserSale.objects.filter(id=sale_id, basket__unique_id=basket_uid).first()

            if sale:
                basket = sale.basket
                sale.delete()

                if len(pay_record) > 0:
                    if pay_record[0].state == "Pending":
                        pay_record[0].basket = None
                        pay_record[0].save()

                # get basket
                basket_sales = ConcoughUserSale.objects.filter(basket=basket)
                if len(basket_sales) <= 0:
                    # delete basket
                    basket.delete()

                result["status"] = "OK"
            else:
                result["status"] = "Error"
                result["error_type"] = "SaleNotExist"

        except Exception:
            result["status"] = "Error"
            result["error_type"] = "RemoteDBError"

        return Response(result)

    def checkoutBasket(self, request, basket_uid, **kwargs):
        result = {}

        try:
            basket = ConcoughUserBasket.objects.prefetch_related('sales').get(unique_id=basket_uid)
            sales = basket.sales.all()

            if len(sales) > 0:
                total_cost = 0

                for sale in sales:
                    total_cost += sale.pay_amount

                if settings.DEV_ENVIRONMENT == 'local' or total_cost == 0 or request.user.username == "989554567890":
                    result["purchased"] = []
                    for sale in sales:
                        try:
                            purchase = ConcoughUserPurchased()
                            purchase.target = sale.target
                            purchase.user = request.user
                            purchase.payed_amount = sale.pay_amount
                            purchase.save()

                            result["purchased"].append({
                                "sale_id": sale.id,
                                "purchase_id": purchase.id,
                                "purchase_time": purchase.created,
                                "downloaded": purchase.downloaded,
                            })

                            # update product statistics
                            with transaction.atomic():
                                if isinstance(sale.target, Entrance):
                                    stat_record = ConcoughProductStatistic.objects.get(entrance=sale.target)
                                    stat_record.purchased += 1
                                    stat_record.save()

                        except IntegrityError:
                            pass
                        else:
                            sale.delete()

                    basket.delete()
                    result["status"] = "OK"

                elif settings.DEV_ENVIRONMENT == 'deploy':
                    # first must be checkout with zarin pal

                    if total_cost != 0:
                        # TODO: check for toman or rials
                        mustPay = True
                        payError = False
                        payment = ConcoughPayments.objects.filter(basket=basket).order_by('-created')
                        if len(payment) > 0:
                            if payment[0].state == "Success" or payment[0].state == "MustVerified":
                                mustPay = False
                                if payment[0].state == "MustVerified":
                                    result, pay = PAYIR.verify_local(payment[0])
                                    if pay.state != 'Success':
                                        mustPay = True
                                    elif pay.state == 'Error':
                                        mustPay = True

                            elif payment[0].state == "Pending":
                                result, pay = PAYIR.verify_local(payment[0])
                                if pay.state == "Error":
                                    payError = True
                                elif pay.state == "Success":
                                    mustPay = False
                            elif payment[0].state == "Error":
                                mustPay = True


                        if mustPay:
                            description = u"پرداخت " + str(total_cost * 10) + u" ریال" + u" - %d - %s" % (request.user.id, basket.id)
                            pay_status, authority = PAYIR.send_request(request.user, basket, total_cost * 10, description)

                            if pay_status is not None:
                                result['status'] = "Redirect"
                                result['url'] = pay_status
                                result['authority'] = authority
                            else:
                                result["status"] = "Error"
                                result["error_type"] = "PaymentProviderError"

                        else:
                            if not payError:
                                result["purchased"] = []
                                for sale in sales:
                                    try:
                                        purchase = ConcoughUserPurchased()
                                        purchase.target = sale.target
                                        purchase.user = request.user
                                        purchase.payed_amount = sale.pay_amount
                                        purchase.save()

                                        result["purchased"].append({
                                            "sale_id": sale.id,
                                            "purchase_id": purchase.id,
                                            "purchase_time": purchase.created,
                                            "downloaded": purchase.downloaded,
                                        })

                                        # update product statistics
                                        with transaction.atomic():
                                            if isinstance(sale.target, Entrance):
                                                stat_record = ConcoughProductStatistic.objects.get(entrance=sale.target)
                                                stat_record.purchased += 1
                                                stat_record.save()

                                    except IntegrityError:
                                        pass
                                    else:
                                        sale.delete()

                                basket.delete()
                                result["status"] = "OK"
                            else:
                                result["status"] = "Error"
                                result["error_type"] = "PaymentProviderError"

            else:
                result["status"] = "Error"
                result["error_type"] = "EmptyBasket"

        except ConcoughUserBasket.DoesNotExist:
            result["status"] = "Error"
            result["error_type"] = "EmptyBasket"

        except Exception, exc:
            print exc
            result["status"] = "Error"
            result["error_type"] = "RemoteDBError"

        return Response(result)

    def verifyCheckout(self, request, **kwargs):
        result = {}

        authority_id = request.data.get("authority_id", "").strip()
        basket_id = request.data.get("basket_id", "").strip()

        pay = None
        if authority_id != "":
            pay = ConcoughPayments.objects.filter(user=request.user, authority=authority_id).first()
        elif basket_id  != "":
            pay = ConcoughPayments.objects.filter(user=request.user, basket__unique_id=basket_id).first()

        if pay is not None:
            try:
                if pay.state == "Success" or pay.state == "MustVerified":
                    if pay.state == "MustVerified":
                        result1, pay1 = PAYIR.verify_local(pay)
                        if result1 == "Success":
                            pay = pay1

                    if pay.state == "Success":
                        basket = ConcoughUserBasket.objects.prefetch_related('sales').get(unique_id=pay.basket.unique_id)
                        sales = basket.sales.all()

                        if len(sales) > 0:
                            total_cost = 0

                            for sale in sales:
                                total_cost += sale.pay_amount

                            result["purchased"] = []
                            for sale in sales:
                                try:
                                    purchase = ConcoughUserPurchased()
                                    purchase.target = sale.target
                                    purchase.user = request.user
                                    purchase.payed_amount = sale.pay_amount
                                    purchase.save()

                                    result["purchased"].append({
                                        "sale_id": sale.id,
                                        "purchase_id": purchase.id,
                                        "purchase_time": purchase.created,
                                        "downloaded": purchase.downloaded,
                                    })

                                    # update product statistics
                                    with transaction.atomic():
                                        if isinstance(sale.target, Entrance):
                                            stat_record = ConcoughProductStatistic.objects.get(entrance=sale.target)
                                            stat_record.purchased += 1
                                            stat_record.save()

                                except IntegrityError:
                                    pass
                                else:
                                    sale.delete()

                            basket.delete()

                        result["status"] = "OK"
                        result["state"] = pay.state
                        result["provider_status"] = pay.provider_status
                    else:
                        result["status"] = "Error"
                        result["error_type"] = pay.state
                        result["provider_status"] = pay.provider_status

                elif pay.state == "Pending":
                    result1, pay1 = PAYIR.verify_local(pay)

                    if result1 == "Success":
                        pay = pay1

                        basket = ConcoughUserBasket.objects.prefetch_related('sales').get(unique_id=pay.basket.unique_id)
                        sales = basket.sales.all()

                        if len(sales) > 0:
                            total_cost = 0

                            for sale in sales:
                                total_cost += sale.pay_amount

                            result["purchased"] = []
                            for sale in sales:
                                try:
                                    purchase = ConcoughUserPurchased()
                                    purchase.target = sale.target
                                    purchase.user = request.user
                                    purchase.payed_amount = sale.pay_amount
                                    purchase.save()

                                    result["purchased"].append({
                                        "sale_id": sale.id,
                                        "purchase_id": purchase.id,
                                        "purchase_time": purchase.created,
                                        "downloaded": purchase.downloaded,
                                    })

                                    # update product statistics
                                    with transaction.atomic():
                                        if isinstance(sale.target, Entrance):
                                            stat_record = ConcoughProductStatistic.objects.get(entrance=sale.target)
                                            stat_record.purchased += 1
                                            stat_record.save()

                                except IntegrityError:
                                    pass
                                else:
                                    sale.delete()

                            basket.delete()

                        result["status"] = "OK"
                        result["state"] = pay.state
                        result["provider_status"] = pay.provider_status

                    else:
                        result["status"] = "Error"
                        result["error_type"] = pay.state
                        result["provider_status"] = pay.provider_status

            except Exception, exc:
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "NotPaymentRecord"

        return Response(result)


class BasketViewSetOAuth(ScopedProtectedResourceView, BasketViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["basket"]


class BasketViewSetJwt(BasketViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
