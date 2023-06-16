# coding=utf-8
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.utils.datetime_safe import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.helpers.email_handlers import send_email
from api.models import UserBugReport, AppVersionRepo
from digikunkor import settings
from digikunkor.settings import DOWNLOAD_LINKS
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class InviteFriendsViewSet(ViewSet):
    def post(self, request, **kwargs):

        result = {}
        username = request.user
        emails = request.data.get("emails", [])

        normalized_emails = []
        for email in emails:
            normalized_emails.append(User.objects.normalize_email(email))

        try:
            user = User.objects.get(username=username)

            users = User.objects.filter(email__in=normalized_emails)
            in_system_emails = []
            for user in users:
                in_system_emails.append(user.email)

            for email in normalized_emails:
                if email not in in_system_emails:
                    # sending email hear
                    data = {"date": datetime.now(), "fullname": user.get_full_name()}
                    _from = settings.EMAIL_NO_REPLY_ADDR
                    _to = u"%s" % email
                    subject = u"کنکوق: دعوتنامه از دوست شما"
                    template_name = "api/v1/invite"

                    send_email(subject, _from, [_to, ], data, template_name, request)

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

        return Response(result)


class InviteFriendsViewSetOAuth(ScopedProtectedResourceView, InviteFriendsViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["settings"]


class InviteFriendsViewSetJwt(InviteFriendsViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class ReportBugsViewSet(ViewSet):
    def post(self, request, **kwargs):

        result = {}
        username = request.user
        print username

        desc = request.data.get("description", "")
        app_version = request.data.get("app_version", "")
        api_version = request.data.get("api_version", "")
        device_model = request.data.get("device_model", "")
        os_version = request.data.get("os_version", "")

        if desc != "" and app_version != "" and api_version != "" and device_model != "" and os_version != "":
            try:
                user = User.objects.get(username=username)

                report = UserBugReport()
                report.user = user
                report.api_version = api_version
                report.app_version = app_version
                report.device_model = device_model
                report.os_version = os_version
                report.description = desc

                report.save()

                result["status"] = "OK"

            except User.DoesNotExist:
                result["status"] = "Error"
                result["error_type"] = "UserNotExist"
            except MultipleObjectsReturned:
                result["status"] = "Error"
                result["error_type"] = "MultiRecord"
            except Exception, err:
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"
        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


class ReportBugsViewSetOAuth(ScopedProtectedResourceView, ReportBugsViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["settings"]


class ReportBugsViewSetJwt(ReportBugsViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)


class CheckVersionViewSet(ViewSet):
    def get(self, request, device, **kwargs):

        result = {}

        if device != '':
            try:
                record = AppVersionRepo.objects.filter(device=device).order_by('-released').first()
                if record is not None:
                    result["status"] = "OK"
                    result["version"] = record.version
                    result["released"] = record.released
                    result["link"] = DOWNLOAD_LINKS[device]

                else:
                    result["status"] = "Error"
                    result["error_type"] = "EmptyArray"

            except Exception, exc:
                result["status"] = "Error"
                result["error_type"] = "EmptyArray"
        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)


class CheckVersionViewSetOAuth(ScopedProtectedResourceView, CheckVersionViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["settings"]


class CheckVersionViewSetJwt(CheckVersionViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)

