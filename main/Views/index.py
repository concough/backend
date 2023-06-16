from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf

from digikunkor import settings
from main.Forms.AuthForms import _AuthenticationForm, _HomeAuthenticationForm

__author__ = 'abolfazl'


def home(request):
    # if request.user.is_authenticated:
    #     return redirect('main.admin.home')

    form = _HomeAuthenticationForm()
    dev_environment = settings.DEV_ENVIRONMENT
    cdn_prefix = settings.CDN_PREFIX

    d = dict(form=form, denv=dev_environment, cdn_prefix=cdn_prefix)
    d.update(csrf(request))
    return render_to_response("main/website/home.html",
                              d,
                              context_instance=RequestContext(request))
