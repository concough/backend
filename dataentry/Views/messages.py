# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.datetime_safe import datetime
from dataentry.Forms.MessageForms import MessageReplyForm
from dataentry.Helpers import menu_settings
from dataentry.Helpers.email_handlers import send_email
from dataentry.Helpers.mixins import BuildAbsoluteURIMixin
from dataentry.models import TaskMessage, Task
from digikunkor import settings
from main.Helpers.decorators import group_permission_required

__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_message_box', raise_exception=True)
def message_list(request):
    menu_selected = "messages"
    messages_sent = []
    messages_received = []
    filtered = False
    task = None

    page = request.GET.get('page', 1)
    task_id = request.GET.get('tid', -1)

    next_url = request.get_full_path()

    # get user group name
    user_group_names = request.user.groups.all()

    group_list = [grp.name for grp in user_group_names]
    if 'editor' in group_list or 'picture_creator' in group_list:
        pass
    else:
        # show forbidden message
        raise PermissionDenied

    message_list_sent = []
    message_list_received = []
    if task_id == -1:
        # get all messages
        message_list_sent = TaskMessage.objects.filter(form_user=request.user, task__is_hide=False)\
            .prefetch_related('message_type', 'form_user', 'to_user', 'task', 'task__entrance')\
            .order_by('seen', 'seen_time')
        message_list_received = TaskMessage.objects.filter(to_user=request.user, task__is_hide=False)\
            .prefetch_related('message_type', 'form_user', 'to_user', 'task', 'task__entrance')\
            .order_by('seen', 'seen_time')
    else:
        message_list_sent = TaskMessage.objects.filter(task__id=task_id, task__is_hide=False).filter(form_user=request.user)\
            .prefetch_related('message_type', 'form_user', 'to_user', 'task', 'task__entrance')\
            .order_by('seen', 'seen_time')
        message_list_received = TaskMessage.objects.filter(task__id=task_id, task__is_hide=False).filter(to_user=request.user)\
            .prefetch_related('message_type', 'form_user', 'to_user', 'task', 'task__entrance')\
            .order_by('seen', 'seen_time')
        filtered = True
        task = Task.objects.prefetch_related('entrance').get(pk=task_id, is_hide=False)

    paginator_sent = Paginator(message_list_sent, 20)
    paginator_received = Paginator(message_list_received, 20)
    try:
        messages_sent = paginator_sent.page(page)
    except PageNotAnInteger:
        messages_sent = paginator_sent.page(1)
    except EmptyPage:
        messages_sent = paginator_sent.page(paginator_sent.num_pages)

    try:
        messages_received = paginator_received.page(page)
    except PageNotAnInteger:
        messages_received = paginator_received.page(1)
    except EmptyPage:
        messages_received = paginator_received.page(paginator_received.num_pages)

    d = dict(menul=menu_settings.menus, msel=menu_selected, messages_sent=messages_sent, messages_received=messages_received,
             filtered=filtered, tid=task_id, next_url=next_url, task=task)
    return render_to_response("dataentry/de_messages/messages.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_message_box', raise_exception=True)
def message_reply(request, pk):
    menu_selected = "messages"
    has_error = False
    error_no = -1
    form = None
    message = None

    next_url = request.GET.get('next', None)

    # find task associated
    try:
        message = TaskMessage.objects.prefetch_related('task', 'task__entrance').get(pk=pk, task__is_hide=False)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == 'GET':
            form = MessageReplyForm()

        elif request.method == 'POST':
            form = MessageReplyForm(request.POST, request.FILES)

            if form.is_valid():
                record = form.save(commit=False)
                record.form_user = request.user
                record.task = message.task
                record.to_user = message.form_user
                record.save()

                # sending email notifications
                abs_url = BuildAbsoluteURIMixin()

                data = {"message": record,
                    "link": abs_url.reverse_absolute_uri("admin.messages")}
                _from = settings.EMAIL_NO_REPLY_ADDR
                _to = u"%s <%s>" % (record.to_user.get_full_name(), record.to_user.email)
                subject = u"پیغام جدید"
                template_name = "new_message_operator"

                send_email(subject, _from, [_to, ], data, template_name, request)

                full_redirect_url = "%s?%s" % (reverse('dataentry.messages'), "tid=%d" % message.task.id)
                return redirect(full_redirect_url)

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form,
             message=message, next_url=next_url, err=has_error, error_no=error_no)
    d.update(csrf(request))
    return render_to_response("dataentry/de_messages/message_reply.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_message_box', raise_exception=True)
def message_seen(request, pk):
    try:
        message = TaskMessage.objects.prefetch_related('task').get(pk=pk, task__is_hide=False)
        task_id = message.task.id
        message.seen = True
        message.seen_time = datetime.now()
        message.save()

        full_redirect_url = "%s?%s" % (reverse('dataentry.messages'), "tid=%d" % task_id)
        return redirect(full_redirect_url)
    except:
        pass

    return redirect('dataentry.messages')

