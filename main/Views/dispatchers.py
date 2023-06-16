from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

__author__ = 'abolfazl'

@login_required
def admin_dispatcher(request):
    user = request.user
    groups = [item.name for item in user.groups.all()]
    if 'administrator' in groups or 'master_operator' in groups or 'editor' in groups or 'picture_creator' in groups\
            or 'check_in' in groups or 'reporter' in groups:
        return redirect('admin.home')
    # elif 'editor' in groups or 'picture_creator' in groups:
    #     return redirect('dataentry.home')
    else:
        return redirect('main.auth.logout')