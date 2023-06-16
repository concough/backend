# coding=utf-8
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.utils.datetime_safe import date, datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from api.helpers.email_handlers import send_email
from api.models import Profile
from api.v2.serializers.profile_serializers import ProfileSerializer, GradeSerializer
from digikunkor import settings
from main.models import EntranceType
from oauth2_provider.ext.rest_framework import OAuth2Authentication
from oauth2_provider.views import ScopedProtectedResourceView


class AuthProfileViewSet(ModelViewSet):
    def get(self, request, **kwargs):
        result = {}

        username = request.user

        queryset = Profile.objects.all() \
                       .prefetch_related('user') \
                       .filter(user__id=request.user.id)[:1]
        serializer = ProfileSerializer(queryset, many=True)

        if len(queryset) > 0:
            # profile data exist
            result["status"] = "OK"
            result["record"] = serializer.data

        else:
            result["status"] = "Error"
            result["error_type"] = "ProfileNotExist"

        return Response(result)

    def post(self, request, **kwargs):
        result = {}

        grade = request.data.get("grade", "").strip()
        gender = request.data.get("gender", "").strip()
        firstname = request.data.get("firstname", "").strip()
        lastname = request.data.get("lastname", "").strip()
        birthday_year = request.data.get("byear", 1970)
        birthday_month = request.data.get("bmonth", 1)
        birthday_day = request.data.get("bday", 1)

        if firstname != "" and lastname != "" and grade != "" and gender != "":
            # Update User Profile
            affected = User.objects.filter(pk=request.user.id).update(first_name=firstname,
                                                                      last_name=lastname)
            if affected > 0:
                try:
                    user_record = User.objects.get(pk=request.user.id)
                    # create date

                    if birthday_day <= 0:
                        birthday_day = 1

                    if birthday_month <= 0:
                        birthday_month = 1

                    bdate = date(year=birthday_year, month=birthday_month, day=birthday_day)

                    record, created = Profile.objects.get_or_create(user=request.user,
                                                                    defaults={"grade": grade,
                                                                              "gender": gender,
                                                                              "birthday": bdate})
                    # if created:
                    #     # send email to notify registeration complete
                    #     data = {"date": datetime.now(),}
                    #     _from = settings.EMAIL_INFO_ADDR
                    #     _to = u"%s %s <%s>" % (firstname, lastname, user_record.email)
                    #     subject = u"کنکوق: حساب کاربری با موفقیت ایجاد شد"
                    #     template_name = "api/v1/signup"
                    #
                    #     send_email(subject, _from, [_to, ], data, template_name, request)

                    result["status"] = "OK"
                    result["id"] = record.id
                    result["modified"] = record.modified

                except User.DoesNotExist:
                    result["status"] = "Error"
                    result["error_type"] = "UserNotExist"

                except MultipleObjectsReturned, exp:
                    result["status"] = "Error"
                    result["error_type"] = "MultiRecord"
                except Exception, exc:
                    # print exc
                    result["status"] = "Error"
                    result["error_type"] = "BadData"

            else:
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def update(self, request, **kwargs):
        # type: (object, object) -> object
        result = {}

        grade = request.data.get("grade", "").strip()
        gender = request.data.get("gender", "").strip()
        firstname = request.data.get("firstname", "").strip()
        lastname = request.data.get("lastname", "").strip()
        birthday_year = request.data.get("byear", 1970)
        birthday_month = request.data.get("bmonth", 1)
        birthday_day = request.data.get("bday", 1)

        if firstname != "" and lastname != "" and grade != "" and gender != "":
            # Update User Profile
            affected = User.objects.filter(pk=request.user.id).update(first_name=firstname,
                                                                      last_name=lastname)
            if affected > 0:
                try:
                    # create date

                    if birthday_day <= 0:
                        birthday_day = 1

                    if birthday_month <= 0:
                        birthday_month = 1

                    bdate = date(year=birthday_year, month=birthday_month, day=birthday_day)

                    profile_affected = Profile.objects.filter(user__id=request.user.id).update(
                        grade=grade,
                        gender=gender,
                        birthday=bdate)

                    if profile_affected > 0:
                        result["status"] = "OK"
                    else:
                        result["status"] = "Error"
                        result["error_type"] = "RemoteDBError"

                except MultipleObjectsReturned, exp:
                    result["status"] = "Error"
                    result["error_type"] = "MultiProfile"
                    print exp

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def update_grade(self, request, **kwargs):
        # type: (object, object) -> object
        result = {}

        grade = request.data.get("grade", "").strip()

        if grade != "":
            # Update User Profile
            try:
                profile = Profile.objects.get(user__id=request.user.id)
                profile.grade = grade
                profile.save(force_update=True)

                result["status"] = "OK"
                result["modified"] = profile.modified

            except MultipleObjectsReturned, exp:
                result["status"] = "Error"
                result["error_type"] = "MultiProfile"
            except Exception, exc:
                print(exc)
                result["status"] = "Error"
                result["error_type"] = "RemoteDBError"

        else:
            result["status"] = "Error"
            result["error_type"] = "BadData"

        return Response(result)

    def list_grade(self, request, **kwargs):
        # type: (object, object) -> object
        result = {}

        queryset = EntranceType.objects.all()
        serializer = GradeSerializer(queryset, many=True)

        if len(queryset) > 0:
            # profile data exist
            result["status"] = "OK"
            result["record"] = serializer.data

        else:
            result["status"] = "Error"
            result["error_type"] = "EmptyArray"

        return Response(result)


class AuthProfileViewSetOAuth(ScopedProtectedResourceView, AuthProfileViewSet):
    authentication_classes = [OAuth2Authentication]
    permission_classes = (IsAuthenticated,)

    required_scopes = ["auth"]


class AuthProfileViewSetJwt(AuthProfileViewSet):
    authentication_classes = [JSONWebTokenAuthentication, ]
    permission_classes = (IsAuthenticated,)
