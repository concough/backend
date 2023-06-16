from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from dataentry.Helpers import menu_settings

__author__ = 'abolfazl'

@login_required
def dashboard(request):
    menu_selected = "home"

    d = dict(menul=menu_settings.menus, msel=menu_selected)
    return render_to_response("dataentry/home/dashboard.html", d, context_instance=RequestContext(request))