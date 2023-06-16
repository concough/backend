# coding=utf-8
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.views import login as login_view, password_change
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, User
from django.shortcuts import redirect, render_to_response
from django.template.context_processors import csrf
from django.utils import datetime_safe
from django.utils.datetime_safe import datetime

from api.helpers.sms_handlers import sendSMS, sendCall
from api.models import PreAuth
from digikunkor import settings
from digikunkor.settings import SMS_ALLOWED_IN_DAY, CALL_ALLOWED_IN_DAY
from main.Forms.AuthForms import LoginForm, _PasswordResetForm2, _SetPasswordForm2
from main.models import SmsStatus, SmsCallStatus

__author__ = 'abolfazl'


def login_me2(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return login_view(request, **kwargs)


def change_password(request, **kwargs):
    return password_change(request, **kwargs)


def login_me(request, **kwargs):
    form = None
    has_auth_error = False
    error_msg_code = 0

    next_path = request.GET.get('next', '')

    if request.method == 'GET':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            keep_me_logged_in = form.cleaned_data['keep_me_logged_in']

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if keep_me_logged_in:
                        request.session.set_expiry(settings.KEEP_LOGGED_DURATION)
                        # redirect user

                    if len(next_path) > 0:
                        return redirect(next_path)
                    else:
                        groups = [item.name for item in user.groups.all()]
                        if 'administrator' in groups or 'master_operator' in groups:
                            return redirect('admin.home')
                        elif 'editor' in groups or 'picture_creator' in groups:
                            return redirect('dataentry.home')
                        else:
                            logout(request)
                            error_msg_code = 3  # invalid access
                else:
                    error_msg_code = 1  # inactive user
            else:
                # Return an 'invalid login' error message.
                error_msg_code = -1
                has_auth_error = True

    d = dict(form=form, error_msg_code=error_msg_code, has_auth_error=has_auth_error, next_path=next_path)
    d.update(csrf(request))
    return render_to_response("main/auth/login.html", d)


@login_required
def _logout_me(request):

    logout(request)
    request.session.flush()
    request.user = AnonymousUser

    return redirect('main.auth.login')


def _reset_password(request):
    form = None
    error_msg_code = 0

    dev_environment = settings.DEV_ENVIRONMENT
    cdn_prefix = settings.CDN_PREFIX

    if request.method == 'GET':
        form = _PasswordResetForm2()
    elif request.method == 'POST':
        form = _PasswordResetForm2(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']

            auth_data = User.objects.filter(username=username, is_staff=True).first()
            if auth_data is not None:
                # username does not exist in User Table

                today_min = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.min)
                today_max = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.max)

                sms_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                   created__range=(today_min, today_max),
                                                                   sender_type="sms")
                call_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                    created__range=(today_min, today_max),
                                                                    sender_type="call")

                send_type = "sms"
                if send_type == "sms":
                    if len(sms_statuses_record) < SMS_ALLOWED_IN_DAY:
                        try:
                            rand_number = random.getrandbits(20)
                            user_agent_data = request.META.get('HTTP_USER_AGENT', "")

                            record, created = PreAuth.objects.update_or_create(username=username,
                                                                               auth_type="PASS_RECOVERY",
                                                                               defaults={
                                                                                   "user_agent_data": user_agent_data,
                                                                                   "token": make_password(rand_number),
                                                                                   "approved": False
                                                                                   })

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
                                        sms_status.send_type = "sms"
                                        sms_status.status = response[0]["status"]
                                        sms_status.statustext = response[0]["statustext"]
                                        sms_status.message_id = response[0]["messageid"]

                                        sms_status.save()

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

                            print "%s code = %s" % (username, rand_number)

                            request.session["auth_reset_pass_id"] = record.id
                            request.session["auth_reset_pass_username"] = username

                        except Exception, err:
                            del request.session["auth_reset_pass_id"]
                            print err

                    else:
                        send_type = "call"
                        pass

                if send_type == "call":
                    if len(call_statuses_record) < CALL_ALLOWED_IN_DAY:
                        try:
                            rand_number = random.getrandbits(20)
                            user_agent_data = request.META.get('HTTP_USER_AGENT', "")

                            record, created = PreAuth.objects.update_or_create(username=username,
                                                                               auth_type="PASS_RECOVERY",
                                                                               defaults={
                                                                                   "user_agent_data": user_agent_data,
                                                                                   "token": make_password(rand_number),
                                                                                   "approved": False
                                                                               })

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
                                        sms_status.send_type = "call"
                                        sms_status.status = response[0]["status"]
                                        sms_status.statustext = response[0]["statustext"]
                                        sms_status.message_id = response[0]["messageid"]

                                        sms_status.save()

                                    else:
                                        val = "Error"

                                    pass

                            print "%s code = %s" % (username, rand_number)

                            request.session["auth_reset_pass_id"] = record.id
                            request.session["auth_reset_pass_username"] = username

                        except Exception, err:
                            del request.session["auth_reset_pass_id"]
                            print err

                    else:
                        error_msg_code = 5
                        pass

            else:
                del request.session["auth_reset_pass_id"]
            return redirect("main.auth.passresetdone")

    d = dict(form=form, denv=dev_environment, cdn_prefix=cdn_prefix, error_code=error_msg_code)
    d.update(csrf(request))
    return render_to_response("main/auth/password_reset.html", d)


def _reset_password_done(request):
    form = None
    error_msg_code = 0

    dev_environment = settings.DEV_ENVIRONMENT
    cdn_prefix = settings.CDN_PREFIX

    if request.method == 'GET':
        form = _SetPasswordForm2()
    elif request.method == 'POST':
        if "form_save" in request.POST:
            form = _SetPasswordForm2(request.POST)

            if form.is_valid():
                token = form.cleaned_data['token']
                id = request.session.get("auth_reset_pass_id", -1)

                if id != -1:
                    try:
                        preauth_record = PreAuth.objects.get(pk=id)
                        if check_password(token, preauth_record.token):
                            user = User.objects.get(username=preauth_record.username)

                            form.save(user)

                            del request.session["auth_reset_pass_id"]
                            del request.session["auth_reset_pass_username"]
                            return redirect("main.auth.passresetcomplete")
                        else:
                            # wrong code received
                            error_msg_code = 1
                            pass
                    except:
                        error_msg_code = 2
                        pass
                else:
                    error_msg_code = 3
            else:
                error_msg_code = 4

        elif "resend_code" in request.POST:
            username = request.session.get("auth_reset_pass_username", "")
            if username != "":
                auth_data = User.objects.filter(username=username, is_staff=True).first()
                if auth_data is not None:
                    # username does not exist in User Table

                    today_min = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.min)
                    today_max = datetime.combine(datetime_safe.real_date.today(), datetime_safe.real_time.max)

                    sms_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                       created__range=(today_min, today_max),
                                                                       sender_type="sms")
                    call_statuses_record = SmsCallStatus.objects.filter(username=username,
                                                                        created__range=(today_min, today_max),
                                                                        sender_type="call")

                    send_type = "sms"
                    if send_type == "sms":
                        if len(sms_statuses_record) < SMS_ALLOWED_IN_DAY:
                            try:
                                rand_number = random.getrandbits(20)
                                user_agent_data = request.META.get('HTTP_USER_AGENT', "")

                                record, created = PreAuth.objects.update_or_create(username=username,
                                                                                   auth_type="PASS_RECOVERY",
                                                                                   defaults={
                                                                                       "user_agent_data": user_agent_data,
                                                                                       "token": make_password(rand_number),
                                                                                       "approved": False
                                                                                   })

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
                                            sms_status.send_type = "sms"
                                            sms_status.status = response[0]["status"]
                                            sms_status.statustext = response[0]["statustext"]
                                            sms_status.message_id = response[0]["messageid"]

                                            sms_status.save()

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

                                print "%s code = %s" % (username, rand_number)

                                request.session["auth_reset_pass_id"] = record.id
                                request.session["auth_reset_pass_username"] = username

                            except Exception, err:
                                del request.session["auth_reset_pass_id"]
                                print err

                        else:
                            send_type = "call"
                            pass

                    if send_type == "call":
                        if len(call_statuses_record) < CALL_ALLOWED_IN_DAY:
                            try:
                                rand_number = random.getrandbits(20)
                                user_agent_data = request.META.get('HTTP_USER_AGENT', "")

                                record, created = PreAuth.objects.update_or_create(username=username,
                                                                                   auth_type="PASS_RECOVERY",
                                                                                   defaults={
                                                                                       "user_agent_data": user_agent_data,
                                                                                       "token": make_password(rand_number),
                                                                                       "approved": False
                                                                                   })

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
                                            sms_status.send_type = "call"
                                            sms_status.status = response[0]["status"]
                                            sms_status.statustext = response[0]["statustext"]
                                            sms_status.message_id = response[0]["messageid"]

                                            sms_status.save()

                                        else:
                                            val = "Error"

                                        pass

                                print "%s code = %s" % (username, rand_number)

                                request.session["auth_reset_pass_id"] = record.id
                                request.session["auth_reset_pass_username"] = username

                            except Exception, err:
                                del request.session["auth_reset_pass_id"]
                                print err

                        else:
                            error_msg_code = 5
                            pass

                else:
                    del request.session["auth_reset_pass_id"]
                return redirect("main.auth.passresetcomplete")

    d = dict(form=form, denv=dev_environment, cdn_prefix=cdn_prefix, error_code=error_msg_code)
    d.update(csrf(request))
    return render_to_response("main/auth/password_reset_done.html", d)
