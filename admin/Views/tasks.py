# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.datetime_safe import datetime

from admin.Helpers import menu_settings
from admin.Forms.TaskForms import TaskAddForm, TaskReadyDataEditForm
from admin.Helpers.email_handlers import send_email
from admin.Helpers.mixins import BuildAbsoluteURIMixin
from dataentry.models import Task, ReadyData
from digikunkor import settings
from main.Helpers.decorators import group_permission_required


__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_view_tasks', raise_exception=True)
def task_list(request):
    menu_selected = "tasks"
    user_group_name = None
    tasks = None

    page = request.GET.get('page', 1)

    # get user group name
    user_group_names = request.user.groups.all()

    tasks_list = []
    if 'administrator' in [grp.name for grp in user_group_names]:
        tasks_list = Task.objects.all().prefetch_related('owner', 'user', 'entrance__organization',
                                                         'entrance__entrance_type', 'entrance__entrance_set')
        user_group_name = 'administrator'

    elif 'master_operator' in [grp.name for grp in user_group_names]:
        tasks_list = Task.objects.filter(owner=request.user).prefetch_related('owner', 'user', 'entrance__organization',
                                                         'entrance__entrance_type', 'entrance__entrance_set')

        user_group_name = 'master_operator'
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

    d = dict(menul=menu_settings.menus, msel=menu_selected, tasks=tasks, ugn=user_group_name)
    return render_to_response("admin/de_tasks/task_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_create_task', raise_exception=True)
def task_add(request):
    menu_selected = "tasks"
    form = None
    user_group_name = None

    has_form_message = False
    form_message = -1

    user_group_names = request.user.groups.all()
    group_list = [grp.name for grp in user_group_names]

    if 'administrator' in group_list:
        user_group_name = 'administrator'
    elif 'master_operator' in group_list:
        user_group_name = 'master_operator'

    if request.method == 'GET':
        form = TaskAddForm()
    elif request.method == 'POST':
        form = TaskAddForm(request.POST or None)

        if form.is_valid():
            try:
                task = form.save(commit=False)
                if user_group_name == 'master_operator':
                    task.owner = request.user

                task.save()

                entrance = task.entrance
                entrance.assigned_to_task = True
                entrance.save()

                # create ready data records
                booklets = task.entrance.booklets.all()
                for booklet in booklets:
                    booklet_details = booklet.bookletdetails.all()
                    for bd in booklet_details:
                        rd = ReadyData(task=task, entrance_booklet_detail=bd)
                        rd.save()

                # sending emails to user
                abs_url = BuildAbsoluteURIMixin()

                data = {"entrance": entrance, "date": datetime.now(), "owner": task.owner,
                    "link": abs_url.reverse_absolute_uri("dataentry.tasks.details", pk=task.id)}
                _from = settings.EMAIL_NO_REPLY_ADDR
                _to = u"%s <%s>" % (task.user.get_full_name(), task.user.email)
                subject = u"وظیفه جدید"
                template_name = "new_task_operator"

                send_email(subject, _from, [_to, ], data, template_name, request)

                if user_group_name == 'administrator':
                    # sending mail to master

                    data = {"entrance": entrance, "date": datetime.now(), "operator": task.user,
                        "link": abs_url.reverse_absolute_uri("admin.tasks.details", pk=task.id)}
                    _from = settings.EMAIL_NO_REPLY_ADDR
                    _to = u"%s <%s>" % (task.owner.get_full_name(), task.owner.email)
                    subject = u"وظیفه جدید"
                    template_name = "new_task_master"

                    send_email(subject, _from, [_to, ], data, template_name, request)

                return redirect('admin.tasks')
            except IntegrityError:
                has_form_message = True
                form_message = 1
            except Exception, exc:
                print exc

    if 'master_operator' in group_list and 'administrator' not in group_list:
        form.fields['owner'].widget.attrs['readonly'] = True

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, ugn=user_group_name,
             has_form_message=has_form_message, form_message=form_message)
    d.update(csrf(request))
    return render_to_response("admin/de_tasks/task_add.html", d,
                              context_instance=RequestContext(request))


# @login_required
# @group_permission_required('main.de_create_task', raise_exception=True)
# def task_del(request, pk):
#     try:
#         task = Task.objects.get(pk=pk)
#
#         task.r_data.all().delete()
#
#         task.entrance.assigned_to_task = False
#         task.entrance.save()
#
#         task.delete()
#     except Exception, exc:
#         pass
#
#     return redirect('admin.tasks')


@login_required
@group_permission_required('main.de_create_task', raise_exception=True)
def task_del(request, pk):
    try:
        task = Task.objects.get(pk=pk)
        task.is_hide = True
        task.save()

    except Exception, exc:
        pass

    return redirect('admin.tasks')


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
                                                         'entrance__entrance_type', 'entrance__entrance_set').get(pk=pk)
    except Exception, exc:
        has_error = True
        error_no = 1

    if not has_error:
        data_records = ReadyData.objects.filter(task=task).prefetch_related('entrance_booklet_detail__lesson')

    d = dict(menul=menu_settings.menus, msel=menu_selected,
             task=task, data_records=data_records, err=has_error, error_no=error_no)
    return render_to_response("admin/de_tasks/task_detail_list.html", d,
                              context_instance=RequestContext(request))
