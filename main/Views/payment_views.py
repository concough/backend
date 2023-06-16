from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import render_to_response
from django.template import Template
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

from api.helpers.paymets.payir_payment import PAYIR
from api.helpers.paymets.zarinpal_payment import ZarinPal
from api.helpers.sms_handlers import sendSMS
from main.models import ConcoughUserBasket, ConcoughUserPurchased, Entrance, ConcoughProductStatistic


@csrf_exempt
def zarinpal_verify(request, unique_id):
    result, pay = ZarinPal.verify(request, unique_id)

    ref_id = pay.ref_id

    if result == "Success":
        try:
            basket = ConcoughUserBasket.objects.prefetch_related('sales').get(unique_id=pay.basket.id)
            sales = basket.sales.all()

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

                sendSMS("kavenegar", basket.user.username, total_cost, "checkout")
                basket.delete()

        except Exception, exc:
            result = "Error"

    d = dict(ref_id=ref_id, result=result)
    return render_to_response('main/website/pay_result.html', d)


@csrf_exempt
def payir_verify(request, unique_id):

    # result = "Success"
    # d = dict(ref_id=None, result=result)
    # return render_to_response('main/website/pay_result.html', d)

    try:
        result, pay = PAYIR.verify(request, unique_id)
        if result == "Success":
            basket = ConcoughUserBasket.objects.prefetch_related('sales').get(unique_id=pay.basket.unique_id)
            sales = basket.sales.all()

            if len(sales) > 0:
                total_cost = 0

                for sale in sales:
                    total_cost += sale.pay_amount

                # for sale in sales:
                #     try:
                #         purchase = ConcoughUserPurchased()
                #         purchase.target = sale.target
                #         purchase.user = request.user
                #         purchase.payed_amount = sale.pay_amount
                #         purchase.save()
                #
                #
                #         # update product statistics
                #         with transaction.atomic():
                #             if isinstance(sale.target, Entrance):
                #                 stat_record = ConcoughProductStatistic.objects.get(entrance=sale.target)
                #                 stat_record.purchased += 1
                #                 stat_record.save()
                #
                #     except IntegrityError:
                #         pass
                #     else:
                #         sale.delete()

                sendSMS("kavenegar", basket.user.username, total_cost, "checkout")
                # basket.delete()

    except Exception, exc:
        result = "Error"

    d = dict(ref_id=None, result=result)
    return render_to_response('main/website/pay_result.html', d, context_instance=RequestContext(request))


@csrf_exempt
def pv(request):
    d = dict(ref_id=None, result="Success")
    return render_to_response('main/website/pay_result.html', d, context_instance=RequestContext(request))