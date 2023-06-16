from kavenegar import *

from digikunkor.settings import SMS_KAVENEGAR_API_KEY, SMS_KAVENEGAR_SIGNUP_SMS_TEMPLATE, \
    SMS_KAVENEGAR_PASS_SMS_TEMPLATE, SMS_KAVENEGAR_PASS_CALL_TEMPLATE, SMS_KAVENEGAR_SIGNUP_CALL_TEMPLATE, \
    SMS_KAVENEGAR_CHECKOUT_SMS_TEMPLATE, SMS_KAVENEGAR_BUG_REPORT_SMS_TEMPLATE, \
    SMS_KAVENEGAR_EDITOR_PAYMENT_SMS_TEMPLATE


class KavenegarSMSProvider:
    __api_key = SMS_KAVENEGAR_API_KEY

    def __init__(self):
        pass

    def sendSMS(self, to, token, tmpl="signup"):
        sms_template = SMS_KAVENEGAR_SIGNUP_SMS_TEMPLATE
        if tmpl == "pass":
            sms_template = SMS_KAVENEGAR_PASS_SMS_TEMPLATE
        elif tmpl == "checkout":
            sms_template = SMS_KAVENEGAR_CHECKOUT_SMS_TEMPLATE
        elif tmpl == "bug_report":
            sms_template = SMS_KAVENEGAR_BUG_REPORT_SMS_TEMPLATE

        try:
            api = KavenegarAPI(self.__api_key)
            params = {
                'receptor': to,
                'template': sms_template,
                'token': token,
                'type': 'sms',  # sms vs call
            }
            response = api.verify_lookup(params)
            return response

        except APIException as e:
            return None
        except HTTPException as e:
            return None

    def sendSMS2(self, to, token1, token2, tmpl="signup"):
        sms_template = SMS_KAVENEGAR_SIGNUP_SMS_TEMPLATE
        if tmpl == "pass":
            sms_template = SMS_KAVENEGAR_PASS_SMS_TEMPLATE
        elif tmpl == "checkout":
            sms_template = SMS_KAVENEGAR_CHECKOUT_SMS_TEMPLATE
        elif tmpl == "bug_report":
            sms_template = SMS_KAVENEGAR_BUG_REPORT_SMS_TEMPLATE
        elif tmpl == "editor_payment":
            sms_template = SMS_KAVENEGAR_EDITOR_PAYMENT_SMS_TEMPLATE

        try:
            api = KavenegarAPI(self.__api_key)
            params = {
                'receptor': to,
                'template': sms_template,
                'token': token1,
                "token2": token2,
                'type': 'sms',  # sms vs call
            }
            response = api.verify_lookup(params)
            return response

        except APIException as e:
            return None
        except HTTPException as e:
            return None

    def sendCall(self, to, token, tmpl="signup"):
        call_template = SMS_KAVENEGAR_SIGNUP_CALL_TEMPLATE
        if tmpl == "pass":
            call_template = SMS_KAVENEGAR_PASS_CALL_TEMPLATE

        try:
            api = KavenegarAPI(self.__api_key)
            params = {
                'receptor': to,
                'template': call_template,
                'token': token,
                'type': 'call',  # sms vs call
            }
            response = api.verify_lookup(params)
            return response

        except APIException as e:
            return None
        except HTTPException as e:
            return None

    def smsStatus(self, message_id):
        try:
            api = KavenegarAPI(self.__api_key)
            params = {
                'messageid': message_id
            }

            response = api.sms_status(params)
            return response

        except APIException as e:
            return None
        except HTTPException as e:
            return None

    def callStatus(self, message_id):
        try:
            api = KavenegarAPI(self.__api_key)
            params = {
                'messageid': message_id
            }

            response = api.call_status(params)
            return response

        except APIException as e:
            return None
        except HTTPException as e:
            return None

