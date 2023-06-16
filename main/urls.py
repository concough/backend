from digikunkor import settings
from main.Forms.AuthForms import _AuthenticationForm, _PasswordChangeForm, _PasswordResetForm, _SetPasswordForm
from main.Views.auth import login_me2, _logout_me, _reset_password, _reset_password_done
from django.contrib.auth import views as auth_views
from main.Views.dispatchers import admin_dispatcher
from main.Views.index import home
from main.Views.payment_views import zarinpal_verify, payir_verify, pv

__author__ = 'abolfazl'

from django.conf.urls import url

urlpatterns = (# url(r'^login$', login_me, name="main.auth.login"),
               url(r'^login/?$', login_me2, {
                   'template_name': 'main/auth/login.html',
                                            'authentication_form': _AuthenticationForm,
                                            'extra_context': {'denv': settings.DEV_ENVIRONMENT, "cdn_prefix": settings.CDN_PREFIX}},
                   name="main.auth.login"),
               #                      url(r'^logout$', _logout_me, name="main.auth.logout"),
               url(r'^logout/?$', auth_views.logout, {'next_page': 'main.auth.login'}, name="main.auth.logout"),
               url(r'^passchange/?$', auth_views.password_change, {'password_change_form': _PasswordChangeForm,
                                                                  'template_name': 'main/auth/password_change.html',
                                                                  'post_change_redirect': 'main.auth.passchangedone',
                                                                  'extra_context': {'msel': 'None'}},
                   name="main.auth.passchange"),
               url(r'^passchange/done/?$', auth_views.password_change_done, {
                   'template_name': 'main/auth/password_change_done.html',
                   'extra_context': {'msel': 'None'}}, name="main.auth.passchangedone"),
               # url(r'^passreset/?$', auth_views.password_reset,
               #     {'template_name': 'main/auth/password_reset.html',
               #      'email_template_name': 'emails/auth/password_reset.txt',
               #      'subject_template_name': 'emails/auth/password_reset_subject.txt',
               #      'html_email_template_name': 'emails/auth/password_reset.html',
               #      'password_reset_form': _PasswordResetForm,
               #      'post_reset_redirect': 'main.auth.passresetdone',
               #      'from_email': settings.EMAIL_NO_REPLY_ADDR,
               #      'extra_context': {'denv': settings.DEV_ENVIRONMENT, "cdn_prefix": settings.CDN_PREFIX}}, name="main.auth.passreset"),
               url(r'^passreset/?$', _reset_password, name="main.auth.passreset"),
               # url(r'^passreset/done/?$', auth_views.password_reset_done, {
               #     'template_name': 'main/auth/password_reset_done.html',
               #     'extra_context': {'denv': settings.DEV_ENVIRONMENT, "cdn_prefix": settings.CDN_PREFIX}}, name="main.auth.passresetdone"),
               url(r'^passreset/done/?$', _reset_password_done, name="main.auth.passresetdone"),
    #            url(
    #                r'^passreset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/?$',
    #                auth_views.password_reset_confirm, {'template_name': 'main/auth/password_reset_confirm.html',
    #                                                    'set_password_form': _SetPasswordForm,
    #                                                    'post_reset_redirect': 'main.auth.passresetcomplete',
    #                                                                           'extra_context': {
    # 'denv': settings.DEV_ENVIRONMENT, "cdn_prefix": settings.CDN_PREFIX}},
    #                name="main.auth.passresetconfirm"),
               url(r'^passreset/complete/?$', auth_views.password_reset_done, {
                   'template_name': 'main/auth/password_reset_complete.html',
               }, name="main.auth.passresetcomplete"),
               url(r'^index/?$', admin_dispatcher, name="main.admin.home"),
               url(r'^pay/verify/zarin/(?P<unique_id>[0-9a-fA-F]{32})/?$', zarinpal_verify, name='main.pay_verify.zarin'),
               url(r'^pay/verify/payir/(?P<unique_id>[0-9a-fA-F]{32})/?$', payir_verify, name='main.pay_verify.payir'),
               # url(r'^pay/verify/payir/?$', payir_verify, name='main.pay_verify.payir'),
               # url(r'^pv/?$', pv, name='main.pay_verify.payir'),
               url(r'^$', home, name="main.home"),

               )
