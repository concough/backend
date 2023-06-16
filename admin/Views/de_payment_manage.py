from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf

from admin.Forms.DEPaymentProviderForms import PaymentProviderAddForm
from admin.Helpers import menu_settings
from admin.Helpers.settings_menu_settings import settings_menus
from main.Helpers.decorators import group_permission_required
from main.models import PaymentProvider


@login_required
@group_permission_required('main.de_payment_manage', raise_exception=True)
def payment_provider_list(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_payments"

    payment_providers = PaymentProvider.objects.all()

    d = dict(menul=menu_settings.menus, msel=menu_selected, pps=payment_providers, minnersel=inner_menu_selected, menuinner=settings_menus)
    return render_to_response("admin/de_payment_manage/payment_provider_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_payment_manage', raise_exception=True)
def payment_provider_del(request, pk):
    try:
        obj = PaymentProvider.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.payment_manage.providers")


@login_required
@group_permission_required('main.de_payment_manage', raise_exception=True)
def payment_provider_add(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_payments"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == "GET":
        form = PaymentProviderAddForm()
    elif request.method == "POST":
        form = PaymentProviderAddForm(request.POST or None, request.FILES)

        if form.is_valid():
            try:
                entrance = form.save()
                return redirect('admin.payment_manage.providers')
            except IntegrityError:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, has_form_message=has_form_message,
             form_message=form_message, minnersel=inner_menu_selected, menuinner=settings_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_payment_manage/payment_provider_add.html", d, context_instance=RequestContext(request))
