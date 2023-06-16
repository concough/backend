# coding=utf-8
from main.models import PaymentProvider, ConcoughPayments

import requests

try:
    import json
except ImportError:
    import simplejson as json


class APIException(Exception):
    pass


class HTTPException(Exception):
    pass


class PAYIR:

    @staticmethod
    def send_request(user, basket, amount, description):
        try:
            payment_provider = PaymentProvider.objects.get(name="payir")

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'charset': 'utf-8'
            }

            params = {
                "api": payment_provider.mmerchant_id,
                "amount": amount,
                "redirect": payment_provider.callback_url + basket.unique_id.hex + "/",
                "factorNumber": description
            }
            # params = {
            #     "api": payment_provider.mmerchant_id,
            #     "amount": 10000,
            #     "redirect": payment_provider.callback_url + "12345678901234567890123456789012" + "/",
            #     "factorNumber": u"tاکتور ۱"
            # }

            try:
                result = requests.post(payment_provider.pay_url + "send", headers=headers, auth=None, data=params)
                if result.status_code == 200:
                    data = json.loads(result.content.decode("utf-8"))
                    pay_status = data["status"]

                    if pay_status == 1:
                        transactionId = data["transId"]

                        pay = ConcoughPayments()
                        pay.user = user
                        pay.basket = basket
                        pay.amount = amount
                        pay.description = description
                        pay.authority = transactionId
                        pay.provider = payment_provider
                        pay.state = "Pending"
                        pay.save()

                        path = payment_provider.pay_url + "gateway/" + str(transactionId)
                        return path, transactionId

                    else:
                        print pay_status
                        pay = ConcoughPayments()
                        pay.user = user
                        pay.basket = basket
                        pay.amount = amount
                        pay.description = description
                        pay.provider = payment_provider
                        pay.authority = data["errorCode"]
                        pay.state = "StartError"
                        pay.save()

                else:
                    pass

            except requests.exceptions.RequestException as e:
                pass

            return None, -1

        except Exception, exc:
            print exc
            return None, -1

    @staticmethod
    def verify(request, unique_id):
        payment_provider = PaymentProvider.objects.get(name="payir")

        #print request
        status = int(request.POST.get('status', -1))
        if status == 1:

            transactionId = int(request.POST.get('transId', 0))

            if transactionId != 0:
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'charset': 'utf-8'
                }

                params = {
                    "api": payment_provider.mmerchant_id,
                    "transId": transactionId
                }
                # params = {
                #     "api": payment_provider.mmerchant_id,
                #     "transId": 6748985
                # }
                try:
                    pay = ConcoughPayments.objects.get(basket__unique_id=unique_id, authority=transactionId,
                                                       state__in=["Pending", "MustVerified"])
                    pay.state = "MustVerified"
                    pay.save()

                    result = requests.post(payment_provider.pay_url + "verify", headers=headers, auth=None, data=params)

                    if result.status_code == 200:
                        data = json.loads(result.content.decode("utf-8"))
                        pay_status = data["status"]

                        if pay_status == 1:
                            pay.state = "Success"
                            pay.provider_status = "Success"
                            pay.save()

                            return "Success", pay

                        else:
                            pay.state = "Error"
                            pay.provider_status = str(pay_status["errorMessage"])
                            pay.basket = None
                            pay.save()

                            return "Error", pay
                    else:
                        try:
                            data = json.loads(result.content.decode("utf-8"))
                            pay_status = data["status"]

                            pay.state = "Error"
                            pay.provider_status = str(pay_status["errorMessage"])
                            pay.basket = None
                            pay.save()

                            return "Error", pay

                        except:
                            pay.state = "Error"
                            pay.provider_status = "HTTPERROR %s" % str(result.status_code)
                            pay.basket = None
                            pay.save()

                            return "Error", pay

                except Exception, exc:
                    if pay:
                        pay.state = "Error"
                        pay.provider_status = "Cancel"
                        pay.basket = None
                        pay.save()

                    print exc
                    pass
            else:
                pass
        else:
            pass
        return "Error", None


    @staticmethod
    def verify_local(pay):
        payment_provider = PaymentProvider.objects.get(name="payir")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

        params = {
            "api": payment_provider.mmerchant_id,
            "transId": pay.authority
        }
        try:
            pay.state = "MustVerified"
            pay.save()

            result = requests.post(payment_provider.pay_url + "verify", headers=headers, auth=None, data=params)

            if result.status_code == 200:
                data = json.loads(result.content.decode("utf-8"))
                pay_status = data["status"]

                if pay_status == 1:
                    pay.state = "Success"
                    pay.provider_status = str("Success")
                    pay.save()

                    return "Success", pay
                else:
                    pay.state = "Error"
                    pay.provider_status = str(pay_status["errorMessage"])
                    pay.basket = None
                    pay.save()
            else:
                try:
                    data = json.loads(result.content.decode("utf-8"))
                    pay_status = data["status"]

                    pay.state = "Error"
                    pay.provider_status = str(pay_status["errorMessage"])
                    pay.basket = None
                    pay.save()

                    return "Error", pay

                except:
                    pay.state = "Error"
                    pay.provider_status = "HTTPERROR %s" % str(result.status_code)
                    pay.basket = None
                    pay.save()

                    return "Error", pay

        except Exception, exc:
            pass

        return "Error", None
