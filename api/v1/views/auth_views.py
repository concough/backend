# coding=utf-8
import random

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User, Group
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction
from django.utils import datetime_safe
from django.utils.datetime_safe import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.helpers.email_handlers import send_email
from api.helpers.sms_handlers import sendSMS, sendCall
from api.models import PreAuth, Profile, UserRegisteredDevice
from digikunkor import settings
from digikunkor.settings import SITE_NAME, SMS_ALLOWED_IN_DAY, CALL_ALLOWED_IN_DAY
from main.models import SmsStatus, SmsCallStatus
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class AuthPreCheckUsernameViewSet(ViewSet):
    def post(self, request, **kwargs):
        result = {}

        username = request.data.get("username", "").strip()
        if username != "":
            try:
                auth_data = User.objects.filter(username=username).first()
                if auth_data is not None:
                    result["status"] = "Error"
                    result["error_type"] = "ExistUsername"
                else:
                    result["status"] = "OK"

            except Exception, err:
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


# class AuthPreSignupViewSet(ViewSet):
#     def post(self, request, **kwargs):
#
#         result = {}
#
#         username = request.data.get("username", "").strip()
#         email = request.data.get("email", "").strip()
#
#         if username != "" and email != "":
#             auth_data = User.objects.filter(username=username).first()
#             if auth_data is None:
#                 # username does not exist in User Table
#                 try:
#                     # create token first
#                     rand_number = random.getrandbits(20)
#                     user_agent_data = self.request.META.get('HTTP_USER_AGENT', "")
#
#                     record, created = PreAuth.objects.update_or_create(email=email, username=username,
#                                                                        auth_type="SIGNUP",
#                                                                        defaults={"user_agent_data": user_agent_data,
#                                                                                  "token": rand_number,
#                                                                                  "approved": False
#                                                                                  })
#
#                     if created:
#                         result["status"] = "OK"
#                         result["id"] = record.id
#                     else:
#                         # the record is returned
#                         result["status"] = "OK"
#                         result["id"] = record.id
#
#                     # sending email hear
#                     data = {"date": record.created, "rnumber": rand_number}
#                     _from = settings.EMAIL_INFO_ADDR
#                     _to = u"%s <%s>" % (username, email)
#                     subject = u"کنکوق: کد فعالسازی"
#                     template_name = "api/v1/pre_signup"
#
#                     send_email(subject, _from, [_to, ], data, template_name, request)
#
#                 except Exception, err:
#                     print err
#                     result["status"] = "Error"
#                     result["error_type"] = "RemoteDBError"
#
#             else:
#                 result["status"] = "Error"
#                 result["error_type"] = "ExistUsername"
#
#         else:
#             result["status"] = "Error"
#             result["error_type"] = "BadData"
#
#         return Response(result)


class AuthPreSignupViewSet(ViewSet):
    def post(self, request, **kwargs):

        result = {}

        print request.data
        username = request.data.get("username", "").strip()
        send_type = request.data.get("type", "").strip()

        if username != "":
            # check for signup

            auth_data = User.objects.filter(username=username).first()
            if auth_data is None:
                # username does not exist in User Table

                today_min = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.min)
                today_max = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.max)

                sms_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                   created__range=(today_min, today_max),
                                                                   sender_type="sms")
                call_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                    created__range=(today_min, today_max),
                                                                    sender_type="call")

                if send_type == "sms":
                    if len(sms_statuses_record) < SMS_ALLOWED_IN_DAY:
                        try:
                            # create token first
                            rand_number = random.getrandbits(20)
                            user_agent_data = self.request.META.get('HTTP_USER_AGENT', "")

                            email = "%s@%s" % (username, SITE_NAME)

                            record, created = PreAuth.objects.update_or_create(email=email, username=username,
                                                                               auth_type="SIGNUP",
                                                                               defaults={"user_agent_data": user_agent_data,
                                                                                         "token": make_password(str(rand_number)),
                                                                                         "approved": False
                                                                                         })

                            val = "OK"
                            provider = "kavenegar"

                            if settings.DEV_ENVIRONMENT == "deploy":
                                text = "Hello, Welcome to Concough\n\nCode: %d" % rand_number
                                text = "سلام. به کنکوق خوش آمدید.\n\nگذر واژه: %d" % rand_number

                                if provider == "kavenegar":
                                    response = sendSMS(provider, username, rand_number, "signup")

                                    if response is not None:
                                        sms_status = SmsCallStatus()
                                        sms_status.username = username
                                        sms_status.send_type = "SIGNUP"
                                        sms_status.panel_name = provider
                                        sms_status.sender = response[0]["sender"]
                                        sms_status.sender_type = "sms"
                                        sms_status.status = response[0]["status"]
                                        sms_status.statustext = response[0]["statustext"]
                                        sms_status.message_id = response[0]["messageid"]

                                        sms_status.save()

                                        if response[0]["status"] in (4, 5, 1, 10):
                                            result['send_state'] = "Sent"
                                        elif response[0]["status"] in (11, ):
                                            result['send_state'] = "Undelivered"
                                        elif response[0]["status"] in (6, 13, 14):
                                            result['send_state'] = "Failed"

                                    else:
                                        val = "Error"

                                    pass
                                else:
                                    # text = "سلام. به کنکوق خوش آمدید\n\nگذر واژه: %d" % rand_number
                                    # create sms status record
                                    # sms_status = SmsStatus()
                                    # sms_status.username = username
                                    # sms_status.panel_name = "Unknown"
                                    # sms_status.status = "Pending"
                                    # sms_status.send_type = "SIGNUP"
                                    # sms_status.save()
                                    #
                                    # val, panel = sendSMS("payamresan", username, text)
                                    #
                                    # sms_status.panel_name = panel
                                    # sms_status.status = val
                                    # sms_status.save()
                                    pass

                            elif settings.DEV_ENVIRONMENT == "local":
                                sms_status = SmsCallStatus()
                                sms_status.username = username
                                sms_status.send_type = "SIGNUP"
                                sms_status.panel_name = provider
                                sms_status.sender = ""
                                sms_status.sender_type = "sms"
                                sms_status.status = 1
                                sms_status.statustext = ""
                                sms_status.message_id = 1

                                sms_status.save()

                            print "%s code = %s" % (username, rand_number)

                            if val == "OK":
                                result["status"] = "OK"
                                result["id"] = record.id

                            else:
                                result["status"] = "Error"
                                result["error_type"] = "SMSSendError"

                        except Exception, err:
                            print err
                            result["status"] = "Error"
                            result["error_type"] = "RemoteDBError"
                    else:
                        # Exceed for sms sending
                        result["status"] = "Error"
                        result["error_type"] = "ExceedToday"
                elif send_type == "call":
                    if len(call_statuses_record) < CALL_ALLOWED_IN_DAY:
                        try:
                            # create token first
                            rand_number = random.getrandbits(20)
                            user_agent_data = self.request.META.get('HTTP_USER_AGENT', "")

                            email = "%s@%s" % (username, SITE_NAME)

                            record, created = PreAuth.objects.update_or_create(email=email, username=username,
                                                                               auth_type="SIGNUP",
                                                                               defaults={"user_agent_data": user_agent_data,
                                                                                         "token": make_password(
                                                                                             str(rand_number)),
                                                                                         "approved": False
                                                                                         })

                            val = "OK"
                            provider = "kavenegar"

                            if settings.DEV_ENVIRONMENT == "deploy":
                                text = "سلام. به کنکوق خوش آمدید.\n\nگذر واژه: %d" % rand_number

                                if provider == "kavenegar":
                                    response = sendCall(provider, username, rand_number, "signup")

                                    if response is not None:
                                        sms_status = SmsCallStatus()
                                        sms_status.username = username
                                        sms_status.send_type = "SIGNUP"
                                        sms_status.panel_name = provider
                                        sms_status.sender = response[0]["sender"]
                                        sms_status.sender_type = "call"
                                        sms_status.status = response[0]["status"]
                                        sms_status.statustext = response[0]["statustext"]
                                        sms_status.message_id = response[0]["messageid"]

                                        sms_status.save()

                                        if response[0]["status"] in (4, 5, 1, 10):
                                            result['send_state'] = "Sent"
                                        elif response[0]["status"] in (11,):
                                            result['send_state'] = "Undelivered"
                                        elif response[0]["status"] in (6, 13, 14):
                                            result['send_state'] = "Failed"

                                    else:
                                        val = "Error"

                                    pass

                            elif settings.DEV_ENVIRONMENT == "local":
                                sms_status = SmsCallStatus()
                                sms_status.username = username
                                sms_status.send_type = "SIGNUP"
                                sms_status.panel_name = provider
                                sms_status.sender = ""
                                sms_status.sender_type = "call"
                                sms_status.status = 1
                                sms_status.statustext = ""
                                sms_status.message_id = 1

                                sms_status.save()

                            print "%s code = %s" % (username, rand_number)

                            if val == "OK":
                                result["status"] = "OK"
                                result["id"] = record.id

                            else:
                                result["status"] = "Error"
                                result["error_type"] = "CallSendError"

                        except Exception, err:
                            print err
                            result["status"] = "Error"
                            result["error_type"] = "RemoteDBError"
                    else:
                        # Exceed for sms sending
                        result["status"] = "Error"
                        result["error_type"] = "ExceedCallToday"
                else:
                    result["status"] = "Error"
                    result["error_type"] = "ExceedCallToday"
            else:
                result["status"] = "Error"
                result["error_type"] = "ExistUsername"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


# class AuthPreSignupCodeViewSet(ViewSet):
#     def post(self, request, **kwargs):
#
#         result = {}
#
#         username = request.data.get("username", "").strip()
#         email = request.data.get("email", "").strip()
#         password = request.data.get("password", "").strip()
#         id = request.data.get("id", -1)
#         code = request.data.get("code", 0)
#
#         if username != "" and id != -1 and email != "" and password != "":
#             auth_data = PreAuth.objects.filter(username=username, pk=id, token=code).first()
#             if auth_data is None:
#                 # record not exist
#                 result["status"] = "Error"
#                 result["error_type"] = "PreAuthNotExist"
#             else:
#                 print auth_data.approved
#                 if auth_data.approved == 0:
#                     auth_data.approved = True
#                     try:
#                         auth_data.save()
#
#                         # create user instance
#                         simple_group = Group.objects.get(name='simple')
#
#                         created_user = User.objects.create_user(username, email, password)
#                         created_user.is_staff = False
#                         created_user.is_active = True
#                         created_user.groups = [simple_group, ]
#                         created_user.save()
#                         result["status"] = "OK"
#
#                     except IntegrityError, err:
#                         result["status"] = "Error"
#                         result["error_type"] = "ExistUsername"
#
#                     except Exception, err:
#                         print err
#                         result["status"] = "Error"
#                         result["error_type"] = "RemoteDBError"
#
#                 else:
#                     result["status"] = "Error"
#                     result["error_type"] = "ExpiredCode"
#
#         else:
#             result["status"] = "Error"
#             result["error_type"] = "BadData"
#
#         return Response(result)


class AuthPreSignupCodeViewSet(ViewSet):
    def post(self, request, **kwargs):

        result = {}

        username = request.data.get("username", "").strip()
        id = request.data.get("id", -1)
        code = request.data.get("code", 0)

        print username, id, code

        if username != "" and id != -1:
            auth_data = PreAuth.objects.filter(username=username, pk=id).first()
            if auth_data is None:
                # record not exist
                result["status"] = "Error"
                result["error_type"] = "PreAuthNotExist"
            else:
                if auth_data.approved == 0:
                    if check_password(code, auth_data.token):
                        auth_data.approved = True
                        try:
                            auth_data.save()

                            # create user instance
                            simple_group = Group.objects.get(name='simple')

                            password = code
                            email = "%s@%s" % (username, SITE_NAME)

                            created_user = User.objects.create_user(username, email, password)
                            created_user.is_staff = False
                            created_user.is_active = True
                            # created_user = User(username=username, email=email, is_staff=False, is_active=True)
                            # created_user.set_password(password)
                            # created_user.save()
                            created_user.groups = [simple_group, ]
                            created_user.save()
                            result["status"] = "OK"

                        except IntegrityError, err:
                            result["status"] = "Error"
                            result["error_type"] = "ExistUsername"

                        except Exception, err:
                            print err
                            result["status"] = "Error"
                            result["error_type"] = "RemoteDBError"
                    else:
                        result["status"] = "Error"
                        result["error_type"] = "BadData"

                else:
                    result["status"] = "Error"
                    result["error_type"] = "ExpiredCode"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


# class AuthForgotPasswordViewSet(ViewSet):
#     def post(self, request, **kwargs):
#         print("received")
#
#         result = {}
#
#         username = request.data.get("username", "").strip()
#
#         if username != "":
#             auth_data = User.objects.filter(username=username).first()
#             if auth_data is not None:
#                 # username does not exist in User Table
#                 try:
#                     # create token first
#                     rand_number = random.getrandbits(20)
#                     user_agent_data = self.request.META.get('HTTP_USER_AGENT', "")
#
#                     record, created = PreAuth.objects.update_or_create(username=username,
#                                                                        auth_type="PASS_RECOVERY",
#                                                                        defaults={"user_agent_data": user_agent_data,
#                                                                                  "token": rand_number,
#                                                                                  "approved": False
#                                                                                  })
#
#                     if created:
#                         result["status"] = "OK"
#                         result["id"] = record.id
#                     else:
#                         # the record is returned
#                         result["status"] = "OK"
#                         result["id"] = record.id
#
#                     # sending email hear
#                     data = {"date": record.created, "rnumber": rand_number}
#                     _from = settings.EMAIL_INFO_ADDR
#                     _to = u"%s <%s>" % (username, auth_data.email)
#                     subject = u"کنکوق: بازیابی گذر واژه"
#                     template_name = "api/v1/forgot_password"
#
#                     send_email(subject, _from, [_to, ], data, template_name, request)
#
#                 except Exception, err:
#                     result["status"] = "Error"
#                     result["error_type"] = "RemoteDBError"
#
#             else:
#                 result["status"] = "Error"
#                 result["error_type"] = "UserNotExist"
#
#         else:
#             result["status"] = "Error"
#             result["error_type"] = "BadData"
#
#         return Response(result)


class AuthForgotPasswordViewSet(ViewSet):
    def post(self, request, **kwargs):
        result = {}

        username = request.data.get("username", "").strip()
        send_type = request.data.get("type", "").strip()

        if username != "":
            auth_data = User.objects.filter(username=username).first()
            if auth_data is not None:
                # username does not exist in User Table
                try:
                    # create token first
                    today_min = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.min)
                    today_max = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.max)

                    sms_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                       created__range=(today_min, today_max),
                                                                       sender_type="sms")
                    call_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                        created__range=(today_min, today_max),
                                                                        sender_type="call")


                    if send_type == "sms":
                        if len(sms_statuses_record) < SMS_ALLOWED_IN_DAY:
                            try:
                                # create token first
                                rand_number = random.getrandbits(20)
                                user_agent_data = self.request.META.get('HTTP_USER_AGENT', "")

                                email = "%s@%s" % (username, SITE_NAME)

                                record, created = PreAuth.objects.update_or_create(username=username,
                                                                                   auth_type="PASS_RECOVERY",
                                                                                   defaults={
                                                                                       "user_agent_data": user_agent_data,
                                                                                       "token": make_password(str(rand_number)),
                                                                                       "approved": False
                                                                                       })

                                # record, created = PreAuth.objects.update_or_create(email=email, username=username,
                                #                                                    auth_type="PASS_RECOVERY",
                                #                                                    defaults={
                                #                                                        "user_agent_data": user_agent_data,
                                #                                                        "token": make_password(
                                #                                                            str(rand_number)),
                                #                                                        "approved": False
                                #                                                    })
                                val = "OK"
                                provider = "kavenegar"

                                if settings.DEV_ENVIRONMENT == "deploy":
                                    text = "Hello, Welcome to Concough\n\nCode: %d" % rand_number
                                    text = "سلام. به کنکوق خوش آمدید.\n\nگذر واژه: %d" % rand_number

                                    if provider == "kavenegar":
                                        response = sendSMS(provider, username, rand_number, "pass")

                                        if response is not None:
                                            sms_status = SmsCallStatus()
                                            sms_status.username = username
                                            sms_status.send_type = "PASS_RECOVERY"
                                            sms_status.panel_name = provider
                                            sms_status.sender = response[0]["sender"]
                                            sms_status.sender_type = "sms"
                                            sms_status.status = response[0]["status"]
                                            sms_status.statustext = response[0]["statustext"]
                                            sms_status.message_id = response[0]["messageid"]

                                            sms_status.save()

                                            if response[0]["status"] in (4, 5, 1, 10):
                                                result['send_state'] = "Sent"
                                            elif response[0]["status"] in (11,):
                                                result['send_state'] = "Undelivered"
                                            elif response[0]["status"] in (6, 13, 14):
                                                result['send_state'] = "Failed"

                                        else:
                                            val = "Error"

                                        pass
                                    else:
                                        # text = "سلام. به کنکوق خوش آمدید\n\nگذر واژه: %d" % rand_number
                                        # create sms status record
                                        # sms_status = SmsStatus()
                                        # sms_status.username = username
                                        # sms_status.panel_name = "Unknown"
                                        # sms_status.status = "Pending"
                                        # sms_status.send_type = "SIGNUP"
                                        # sms_status.save()
                                        #
                                        # val, panel = sendSMS("payamresan", username, text)
                                        #
                                        # sms_status.panel_name = panel
                                        # sms_status.status = val
                                        # sms_status.save()
                                        pass

                                elif settings.DEV_ENVIRONMENT == "local":
                                    sms_status = SmsCallStatus()
                                    sms_status.username = username
                                    sms_status.send_type = "PASS_RECOVERY"
                                    sms_status.panel_name = provider
                                    sms_status.sender = ""
                                    sms_status.sender_type = "sms"
                                    sms_status.status = 1
                                    sms_status.statustext = ""
                                    sms_status.message_id = 1

                                    sms_status.save()

                                print "%s code = %s" % (username, rand_number)

                                if val == "OK":
                                    result["status"] = "OK"
                                    result["id"] = record.id

                                else:
                                    result["status"] = "Error"
                                    result["error_type"] = "SMSSendError"

                            except Exception, err:
                                print err
                                result["status"] = "Error"
                                result["error_type"] = "RemoteDBError"
                        else:
                            # Exceed for sms sending
                            result["status"] = "Error"
                            result["error_type"] = "ExceedToday"
                    elif send_type == "call":
                        if len(call_statuses_record) < CALL_ALLOWED_IN_DAY:
                            try:
                                # create token first
                                rand_number = random.getrandbits(20)
                                user_agent_data = self.request.META.get('HTTP_USER_AGENT', "")

                                email = "%s@%s" % (username, SITE_NAME)

                                record, created = PreAuth.objects.update_or_create(username=username,
                                                                                   auth_type="PASS_RECOVERY",
                                                                                   defaults={
                                                                                       "user_agent_data": user_agent_data,
                                                                                       "token": make_password(str(rand_number)),
                                                                                       "approved": False
                                                                                       })
                                # record, created = PreAuth.objects.update_or_create(email=email, username=username,
                                #                                                    auth_type="PASS_RECOVERY",
                                #                                                    defaults={
                                #                                                        "user_agent_data": user_agent_data,
                                #                                                        "token": make_password(
                                #                                                            str(rand_number)),
                                #                                                        "approved": False
                                #                                                    })

                                val = "OK"
                                provider = "kavenegar"

                                if settings.DEV_ENVIRONMENT == "deploy":
                                    text = "سلام. به کنکوق خوش آمدید.\n\nگذر واژه: %d" % rand_number

                                    if provider == "kavenegar":
                                        response = sendCall(provider, username, rand_number, "pass")

                                        if response is not None:
                                            sms_status = SmsCallStatus()
                                            sms_status.username = username
                                            sms_status.send_type = "PASS_RECOVERY"
                                            sms_status.panel_name = provider
                                            sms_status.sender = response[0]["sender"]
                                            sms_status.sender_type = "call"
                                            sms_status.status = response[0]["status"]
                                            sms_status.statustext = response[0]["statustext"]
                                            sms_status.message_id = response[0]["messageid"]

                                            sms_status.save()

                                            if response[0]["status"] in (4, 5, 1, 10):
                                                result['send_state'] = "Sent"
                                            elif response[0]["status"] in (11,):
                                                result['send_state'] = "Undelivered"
                                            elif response[0]["status"] in (6, 13, 14):
                                                result['send_state'] = "Failed"

                                        else:
                                            val = "Error"

                                        pass

                                elif settings.DEV_ENVIRONMENT == "local":
                                    sms_status = SmsCallStatus()
                                    sms_status.username = username
                                    sms_status.send_type = "PASS_RECOVERY"
                                    sms_status.panel_name = provider
                                    sms_status.sender = ""
                                    sms_status.sender_type = "call"
                                    sms_status.status = 1
                                    sms_status.statustext = ""
                                    sms_status.message_id = 1

                                    sms_status.save()

                                print "%s code = %s" % (username, rand_number)

                                if val == "OK":
                                    result["status"] = "OK"
                                    result["id"] = record.id

                                else:
                                    result["status"] = "Error"
                                    result["error_type"] = "CallSendError"

                            except Exception, err:
                                print err
                                result["status"] = "Error"
                                result["error_type"] = "RemoteDBError"
                        else:
                            # Exceed for sms sending
                            result["status"] = "Error"
                            result["error_type"] = "ExceedCallToday"
                    else:
                        result["status"] = "Error"
                        result["error_type"] = "ExceedCallToday"

                except Exception, err:
                    print err
                    result["status"] = "Error"
                    result["error_type"] = "RemoteDBError"

            else:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"


        return Response(result)

# class AuthForgotPasswordResetViewSet(ViewSet):
#     def post(self, request, **kwargs):
#
#         result = {}
#
#         username = request.data.get("username", "").strip()
#         password = request.data.get("password", "").strip()
#         rpassword = request.data.get("rpassword", "").strip()
#         id = request.data.get("id", -1)
#         code = request.data.get("code", 0)
#
#         if username != "" and id != -1 and rpassword != "" and password != "":
#             if password == rpassword:
#                 auth_data = PreAuth.objects.filter(username=username, pk=id, token=code).first()
#                 if auth_data is None:
#                     # record not exist
#                     result["status"] = "Error"
#                     result["error_type"] = "PreAuthNotExist"
#                 else:
#                     if auth_data.approved == 0:
#                         auth_data.approved = True
#                         try:
#                             user = User.objects.get(username=username)
#                             auth_data.save()
#
#                             # update user instance
#                             user.set_password(password)
#                             user.save()
#                             result["status"] = "OK"
#
#                         except User.DoesNotExist:
#                             result["status"] = "Error"
#                             result["error_type"] = "UserNotExist"
#                         except MultipleObjectsReturned:
#                             result["status"] = "Error"
#                             result["error_type"] = "MultiRecord"
#                         except Exception, err:
#                             print err
#                             result["status"] = "Error"
#                             result["error_type"] = "RemoteDBError"
#
#                     else:
#                         result["status"] = "Error"
#                         result["error_type"] = "ExpiredCode"
#             else:
#                 result["status"] = "Error"
#                 result["error_type"] = "MismatchPassword"
#
#         else:
#             result["status"] = "Error"
#             result["error_type"] = "BadData"
#
#         return Response(result)


class AuthForgotPasswordResetViewSet(ViewSet):
    def post(self, request, **kwargs):

        result = {}

        username = request.data.get("username", "").strip()
        password = request.data.get("password", "").strip()
        rpassword = request.data.get("rpassword", "").strip()
        id = request.data.get("id", -1)
        code = request.data.get("code", 0)

        if username != "" and id != -1 and rpassword != "" and password != "":
            if password == rpassword:
                if len(password) >= 6:
                    auth_data = PreAuth.objects.filter(username=username, pk=id).first()
                    if auth_data is None:
                        # record not exist
                        result["status"] = "Error"
                        result["error_type"] = "PreAuthNotExist"
                    else:
                        if auth_data.approved == 0:
                            if check_password(code, auth_data.token):
                                auth_data.approved = True
                                auth_data.save()
                                try:
                                    user = User.objects.get(username=username)

                                    # Change all devices state to False
                                    UserRegisteredDevice.objects.filter(user=user).update(state=False)

                                    # update user instance
                                    user.set_password(password)
                                    user.save()
                                    result["status"] = "OK"

                                except User.DoesNotExist:
                                    result["status"] = "Error"
                                    result["error_type"] = "UserNotExist"
                                except MultipleObjectsReturned:
                                    result["status"] = "Error"
                                    result["error_type"] = "MultiRecord"
                                except Exception, err:
                                    print err
                                    result["status"] = "Error"
                                    result["error_type"] = "RemoteDBError"
                            else:
                                result["status"] = "Error"
                                result["error_type"] = "BadData"

                        else:
                            result["status"] = "Error"
                            result["error_type"] = "ExpiredCode"
                else:
                    result["status"] = "Error"
                    result["error_type"] = "PassCannotChange"

            else:
                result["status"] = "Error"
                result["error_type"] = "MismatchPassword"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


class AuthChangePasswordViewSet(ViewSet):
    def post(self, request, **kwargs):

        result = {}

        username = request.user
        password = request.data.get("oldPass", "").strip()
        rpassword = request.data.get("newPass", "").strip()

        if rpassword != "" and password != "":
            try:
                user = User.objects.get(username=username)
                profile = Profile.objects.get(user__id=request.user.id)

                # update user instance
                if len(password) >= 4:
                    if user.check_password(password):
                        user.set_password(rpassword)
                        user.save()

                        profile.modified = datetime.now()
                        profile.save(force_update=True)

                        result["status"] = "OK"
                        result["modified"] = profile.modified
                    else:
                        result["status"] = "Error"
                        result["error_type"] = "PassCannotChange"
                else:
                    result["status"] = "Error"
                    result["error_type"] = "FieldTooSmall"

            except User.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"
            except MultipleObjectsReturned:
                result["status"] = "Error"
                result["error_type"] = "MultiRecord"
            except Exception, err:
                print err
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


class AuthChangePasswordViewSetOAuth(ScopedProtectedResourceView, AuthChangePasswordViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["auth"]


class AuthChangePasswordViewSetJwt(AuthChangePasswordViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class AuthUserRegisteredDevicesViewSet(ViewSet):
    def create(self, request, **kwargs):
        result = {}

        username = request.user
        device_name = request.data.get("device_name", "").strip()
        device_model = request.data.get("device_model", "").strip()
        device_unique_id = request.data.get("device_unique_id", "").strip()

        if username != "" and device_model != "" and device_name != "" and device_unique_id != "":
            try:
                user = User.objects.get(username=username)

                if username == "989554567890":
                    result["status"] = "OK"
                    result["data"] = {
                        "state": True,
                        "device_unique_id": device_unique_id
                    }
                else:

                    obj, created = UserRegisteredDevice.objects.get_or_create(
                        user=username,
                        device_name=device_name,
                        device_unique_id=device_unique_id,
                        defaults={
                            "device_model": device_model
                        }
                    )

                    # now select all records of this user
                    devices = UserRegisteredDevice.objects.filter(user=username, state=True)
                    if len(devices) == 0:
                        obj.state = True
                        obj.save()

                        result["status"] = "OK"
                        result["data"] = {
                            "state": obj.state,
                            "device_unique_id": device_unique_id
                        }

                    else:
                        if obj.state:
                            result["status"] = "OK"
                            result["data"] = {
                                "state": obj.state,
                                "device_unique_id": device_unique_id
                            }
                        else:

                            result["status"] = "Error"
                            result["error_type"] = "AnotherDevice"
                            result["error_data"] = {
                                "device_name": devices[0].device_name,
                                "device_model": devices[0].device_model,
                            }

            except User.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"
        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def lock(self, request, **kwargs):
        result = {}

        username = request.user
        device_name = request.data.get("device_name", "").strip()
        device_model = request.data.get("device_model", "").strip()
        device_unique_id = request.data.get("device_unique_id", "").strip()
        force = request.data.get("lock", False)

        if username != "" and device_name != "" and device_unique_id != "":
            try:
                user = User.objects.get(username=username)

                if username == "989554567890":
                    result["status"] = "OK"
                    result["data"] = {
                        "state": True,
                        "device_unique_id": device_unique_id
                    }
                else:
                    if force:
                        obj, created = UserRegisteredDevice.objects.get_or_create(
                            user=username,
                            device_name=device_name,
                            device_unique_id=device_unique_id,
                            defaults={
                                "device_model": device_model
                            }
                        )
                        UserRegisteredDevice.objects.filter(user=username).update(state=False)

                    else:
                        obj = UserRegisteredDevice.objects.get(
                            user=username,
                            device_name=device_name,
                            device_unique_id=device_unique_id)

                    # now select all records of this user
                    devices = UserRegisteredDevice.objects.filter(user=username, state=True)
                    if len(devices) == 0:
                        with transaction.atomic():
                            obj.state = True
                            obj.save()

                            result["status"] = "OK"
                            result["data"] = {
                                "state": obj.state,
                                "device_unique_id": device_unique_id
                            }

                    else:
                        if devices[0].device_unique_id == device_unique_id:
                            obj.state = True
                            obj.save()

                            result["status"] = "OK"
                            result["data"] = {
                                "state": obj.state,
                                "device_unique_id": device_unique_id
                            }
                        else:
                            result["status"] = "Error"
                            result["error_type"] = "AnotherDevice"
                            result["error_data"] = {
                                "device_name": devices[0].device_name,
                                "device_model": devices[0].device_model,
                            }

            except User.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"

            except UserRegisteredDevice.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "DeviceNotRegistered"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def acquire(self, request, **kwargs):
        result = {}

        username = request.user
        device_name = request.data.get("device_name", "").strip()
        device_unique_id = request.data.get("device_unique_id", "").strip()

        if username != "" and  device_name != "" and device_unique_id != "":
            try:
                user = User.objects.get(username=username)

                if username == "989554567890":
                    result["status"] = "OK"
                else:
                    obj = UserRegisteredDevice.objects.get(
                        user=username,
                        device_name=device_name,
                        device_unique_id=device_unique_id)

                    with transaction.atomic():
                        obj.state = False
                        obj.save()

                    # now select all records of this user
                    devices = UserRegisteredDevice.objects.filter(user=username, state=True)
                    if len(devices) != 0:
                        result["data"] = {
                            "device_name": devices[0].device_name,
                            "device_model": devices[0].device_model,
                            "device_unique_id": device_unique_id
                        }
                    result["status"] = "OK"

            except User.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"

            except UserRegisteredDevice.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "DeviceNotRegistered"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def state(self, request, **kwargs):
        result = {}

        username = request.user
        device_name = request.data.get("device_name", "").strip()
        device_unique_id = request.data.get("device_unique_id", "").strip()

        if username != "" and device_name != "" and device_unique_id != "":
            try:
                user = User.objects.get(username=username)

                if username == "989554567890":
                    result["status"] = "OK"
                    result["data"] = {
                        "state": True,
                        "device_unique_id": device_unique_id
                    }
                else:
                    obj = UserRegisteredDevice.objects.get(
                        user=username,
                        device_name=device_name,
                        device_unique_id=device_unique_id)

                    devices = UserRegisteredDevice.objects.filter(user=username, state=True)
                    if len(devices) == 0:
                        result["status"] = "OK"
                        result["data"] = {
                            "state": obj.state,
                            "device_unique_id": device_unique_id
                        }
                    else:
                        if devices[0].device_unique_id == device_unique_id:
                            obj.state = True
                            obj.save()

                            result["status"] = "OK"
                            result["data"] = {
                                "state": obj.state,
                                "device_unique_id": device_unique_id
                            }
                        else:
                            result["status"] = "Error"
                            result["error_type"] = "AnotherDevice"
                            result["error_data"] = {
                                "device_name": devices[0].device_name,
                                "device_model": devices[0].device_model,
                            }

            except User.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"

            except UserRegisteredDevice.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "DeviceNotRegistered"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


class AuthUserRegisteredDevicesViewSetOAuth(ScopedProtectedResourceView, AuthUserRegisteredDevicesViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["auth"]


class AuthUserRegisteredDevicesViewSetJwt(AuthUserRegisteredDevicesViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
