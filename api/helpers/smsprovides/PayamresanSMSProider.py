import urllib
import urllib2

from digikunkor.settings import SMS_PAYAMRESAN_USERNAME, SMS_PAYAMRESAN_PASSWORD, SMS_PAYAMRESAN_FROM, \
    SMS_PAYAMRESAN_GET_URL


class PayamresanSMSProvider(object):
    __username = SMS_PAYAMRESAN_USERNAME
    __password = SMS_PAYAMRESAN_PASSWORD
    __from = SMS_PAYAMRESAN_FROM
    __get_url = SMS_PAYAMRESAN_GET_URL

    def __init__(self):
        pass

    def send(self, _to, text):
        values = {
            "Username": self.__username,
            "Password": self.__password,
            "From": self.__from,
            "To": "+" + _to,
            "Text": text
        }

        data = urllib.urlencode(values)
        url = "%s?%s" % (self.__get_url, data)
        response = urllib2.urlopen(url)
        html = response.read()
        return html

