import urllib
import urllib2

from api.helpers.smsprovides.KavenegarSMSProvider import KavenegarSMSProvider
from api.helpers.smsprovides.PayamresanSMSProider import PayamresanSMSProvider


def sendSMS(provider, to, text, tmpl="signup"):
    if provider == "kavenegar":
        sender = KavenegarSMSProvider()
        return sender.sendSMS(to, text, tmpl)

    else:
        sender = PayamresanSMSProvider()

        return_value = sender.send(to, text)
        if return_value == "Err":
            return "Error", "payam-resan"
        else:
            return "OK", "payam-resan"


def sendSMS2(provider, to, text1, text2, tmpl="signup"):
    if provider == "kavenegar":
        sender = KavenegarSMSProvider()
        return sender.sendSMS2(to, text1, text2, tmpl)

    else:
        sender = PayamresanSMSProvider()

        return_value = sender.send(to, text1)
        if return_value == "Err":
            return "Error", "payam-resan"
        else:
            return "OK", "payam-resan"


def sendCall(provider, to, text, tmpl="signup"):
    if provider == "kavenegar":
        sender = KavenegarSMSProvider()
        return sender.sendCall(to, text, tmpl)


def checkStatus(provider, msgId, stype):
    if provider == "kavenegar":
        sender = KavenegarSMSProvider()

        if stype == "sms":
            return sender.smsStatus(msgId)
        elif stype == "call":
            return sender.callStatus(msgId)