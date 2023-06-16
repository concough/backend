# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf

from admin.Forms.DEAppManageForms import AppVersionRepoAddForm
from admin.Helpers import menu_settings, apps_menu_settings
from api.helpers.sms_handlers import sendSMS
from api.models import AppVersionRepo, UserBugReport
from digikunkor import settings
from main.Helpers.decorators import group_permission_required


@login_required
@group_permission_required('main.de_app_manage', raise_exception=True)
def app_version_list(request):
    menu_selected = "apps"
    inner_menu_selected = "apps"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == 'POST':
        form = AppVersionRepoAddForm(request.POST or None)

        if form.is_valid():
            try:
                app_version = form.save(commit=True)

            except Exception, exc:
                has_form_message = True
                form_message = 1

    form = AppVersionRepoAddForm()

    version_list = AppVersionRepo.objects.all().order_by('-released')

    d = dict(menul=menu_settings.menus, msel=menu_selected, versions=version_list, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=apps_menu_settings.apps_menus,)
    d.update(csrf(request))
    return render_to_response("admin/de_app_manage/app_version_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_app_manage', raise_exception=True)
def bug_reports_list(request):
    menu_selected = "apps"
    inner_menu_selected = "bugs_report"

    page = request.GET.get('page', 1)
    bugs_list = UserBugReport.objects.all().prefetch_related('user').order_by('-created').order_by('-replyed')

    paginator = Paginator(bugs_list, 20)
    try:
        bugs = paginator.page(page)
    except PageNotAnInteger:
        bugs = paginator.page(1)
    except EmptyPage:
        bugs = paginator.page(paginator.num_pages)

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected, menuinner=apps_menu_settings.apps_menus, bugs=bugs)
    return render_to_response("admin/de_app_manage/bugs_report_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_app_manage', raise_exception=True)
def app_version_del(request, pk):
    try:
        obj = AppVersionRepo.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.app_manage.versions.list")


@login_required
@group_permission_required('main.de_app_manage', raise_exception=True)
def bug_report_del(request, pk):
    try:
        obj = UserBugReport.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.app_manage.bugs_report.list")

@login_required
@group_permission_required('main.de_app_manage', raise_exception=True)
def bug_report_reply(request, pk):
    try:
        obj = UserBugReport.objects.prefetch_related('user').get(pk=pk)
        provider = "kavenegar"

        if settings.DEV_ENVIRONMENT == "deploy":
            text = obj.user.first_name

            if provider == "kavenegar":
                response = sendSMS(provider, obj.user.username, text, "bug_report")

                if response is not None:
                    if response[0]["status"] in (4, 5, 1, 10):
                        obj.replyed = True
                        obj.save()

    except:
        pass

    return redirect("admin.app_manage.bugs_report.list")