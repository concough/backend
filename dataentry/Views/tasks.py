# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.datetime_safe import datetime
from dataentry.Forms.TaskForms import TaskReadyDataEditForm
from dataentry.Helpers import menu_settings
from dataentry.Helpers.email_handlers import send_email
from dataentry.Helpers.mixins import BuildAbsoluteURIMixin
from dataentry.models import Task, ReadyData
from digikunkor import settings
from main.Helpers.decorators import group_permission_required

__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_view_tasks', raise_exception=True)
def task_list(request):
    menu_selected = "tasks"
    tasks = None

    page = request.GET.get('page', 1)

    # get user group name
    user_group_names = request.user.groups.all()

    tasks_list = []
    group_list = [grp.name for grp in user_group_names]

    if 'editor' in group_list:
        tasks_list = Task.objects.filter(user=request.user, is_hide=False).prefetch_related('owner', 'user', 'entrance__organization',
                                                                             'entrance__entrance_type',
                                                                             'entrance__entrance_set')
    else:
        # show forbidden message
        raise PermissionDenied

    paginator = Paginator(tasks_list, 20)
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    d = dict(menul=menu_settings.menus, msel=menu_selected, tasks=tasks)
    return render_to_response("dataentry/de_tasks/task_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_ready_data_list', raise_exception=True)
def task_details(request, pk):
    menu_selected = "tasks"
    task = None
    data_records = []
    has_error = False
    error_no = -1

    try:
        task = Task.objects.prefetch_related('owner', 'user', 'entrance__organization',
                                             'entrance__entrance_type', 'entrance__entrance_set').get(pk=pk, is_hide=False)
    except Exception, exc:
        # print exc
        has_error = True
        error_no = 1

    if not has_error:
        data_records = ReadyData.objects.filter(task=task).prefetch_related('entrance_booklet_detail__lesson')

    d = dict(menul=menu_settings.menus, msel=menu_selected,
             task=task, data_records=data_records, err=has_error, error_no=error_no)
    return render_to_response("dataentry/de_tasks/task_detail_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_ready_data_upload', raise_exception=True)
def task_ready_data_upload(request, pk):
    menu_selected = "tasks"
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1
    form = None
    ready_data_record = None

    try:
        ready_data_record = ReadyData.objects.prefetch_related('task', 'task__entrance',
                                                               'entrance_booklet_detail__lesson',
                                                               'task__entrance__organization',
                                                               'task__entrance__entrance_type',
                                                               'task__entrance__entrance_set').get(pk=pk, task__is_hide=False)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == 'GET':
            form = TaskReadyDataEditForm(instance=ready_data_record)
        elif request.method == 'POST':
            form = TaskReadyDataEditForm(request.POST or None, request.FILES, instance=ready_data_record)

            if form.is_valid():
                try:
                    rd_record = form.save(commit=False)
                    rd_record.upload_time = datetime.now()
                    rd_record.save()

                    # sending email notifications
                    abs_url = BuildAbsoluteURIMixin()

                    data = {"record": rd_record, "date": datetime.now(),
                        "link": abs_url.reverse_absolute_uri("admin.tasks.details", pk=rd_record.task.id)}
                    _from = settings.EMAIL_NO_REPLY_ADDR
                    _to = u"%s <%s>" % (rd_record.task.owner.get_full_name(), rd_record.task.owner.email)
                    subject = u"پیغام جدید"
                    template_name = "ready_data_upload"

                    send_email(subject, _from, [_to, ], data, template_name, request)

                    return redirect('dataentry.tasks.details', pk=ready_data_record.task.id)
                except IntegrityError:
                    has_form_message = True
                    form_message = 1
                except Exception, exc:
                    print exc

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, rdr=ready_data_record,
             err=has_error, error_no=error_no, has_form_message=has_form_message, form_message=form_message)
    d.update(csrf(request))
    return render_to_response("dataentry/de_tasks/task_detail_upload.html", d,
                              context_instance=RequestContext(request))
