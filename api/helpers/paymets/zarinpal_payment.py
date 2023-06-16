from django.contrib.auth.models import User
from suds.client import Client

from main.models import PaymentProvider, ConcoughPayments


class ZarinPal:

    @staticmethod
    def send_request(user, basket, amount, description):
        try:
            payment_provider = PaymentProvider.objects.get(name="zarinpal")

            client = Client(payment_provider.webservice_url)
            result = client.service.PaymentRequest(payment_provider.mmerchant_id,
                                                   amount,
                                                   description,
                                                   payment_provider.email,
                                                   payment_provider.phone,
                                                   payment_provider.callback_url + payment_provider.unique_id.hex + "/")
            if result.Status == 100:
                pay = ConcoughPayments()
                pay.user = user
                pay.basket = basket
                pay.amount = amount
                pay.description = description
                pay.authority = result.Authority
                pay.state = "Pending"
                pay.save()

                path = payment_provider.pay_url + result.Authority
                return path, result.Authority
            else:
                pay = ConcoughPayments()
                pay.user = user
                pay.basket = basket
                pay.amount = amount
                pay.description = description
                pay.authority = result.Authority
                pay.state = "StartError"
                pay.save()
                return None, -1

        except Exception, exc:
            return None, -1

    @staticmethod
    def verify(request, unique_id):
        payment_provider = PaymentProvider.objects.get(name="zarinpal")

        client = Client(payment_provider.webservice_url)
        if request.GET.get('Status') == 'OK':
            try:
                pay = ConcoughPayments.objects.get(unique_id=unique_id, authority=request.GET['Authority'], state="Pending")
                result = client.service.PaymentVerification(payment_provider.mmerchant_id,
                                                            request.GET['Authority'],
                                                            pay.amount)
                if result.Status == 100:
                    pay.state = "Success"
                    pay.ref_id = str(result.RefID)
                    pay.provider_status = str(result.Status)
                    pay.save()

                    return "Success", pay

                else:
                    pay.state = "ProviderResult"
                    pay.provider_status = str(result.Status)
                    pay.save()

                    return str(result.Status), pay

            except Exception, exc:
                return "Error", None

        else:
            return "Error", None