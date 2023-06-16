# coding=utf-8
__author__ = 'abolfazl'

YEAR_CHOICES = [(x, x) for x in xrange(1380, 1401)]
MONTH_CHOICES = [(x, x) for x in xrange(1, 13)]

error_messages = {
    'required': u'این فیلد الزامی است',
    'max_length': u'از حد مجاز طولانی تر است',
    'invalid_image': u'فایل ارسالی میبایست عکس باشد',
    'invalid': u'اطلاعات وارد شده اشتباه است',
    'password_incorrect': u'گذر واژه قدیمی نادرست وارد شده است. لطفا دوباره سعی نمایید.',
    'password_mismatch': u'هر دو گذرواژه باید یکسان باشند',
}