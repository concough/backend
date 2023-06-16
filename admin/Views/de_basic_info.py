from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.context_processors import csrf
from admin.Forms.DEBasicInfoForms import OrganizationAddForm, EntranceTypeAddForm, ExaminationGroupAddForm, \
    EntranceSetAddForm, EntranceLessonAddForm, EntranceSubsetAddForm, TaskMessageTypeAddForm, EntranceSetEditForm, \
    EntranceSaleDataAddForm
from admin.Helpers import menu_settings
from admin.Helpers.entrance_menu_settings import entrance_menus
from dataentry.models import TaskMessageType
from main.Helpers.decorators import group_permission_required
from main.models import Organization, EntranceType, ExaminationGroup, EntranceSet, EntranceLesson, EntranceSubset, \
    EntranceSaleData

__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def organization_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == 'POST':
        form = OrganizationAddForm(request.POST or None, request.FILES)

        if form.is_valid():
            try:
                organization = form.save(commit=True)

            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = OrganizationAddForm()

    organization_list = Organization.objects.all()

    d = dict(menul=menu_settings.menus, msel=menu_selected, organizations=organization_list, form=form,
             has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/organization_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def organization_edit(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_error = False
    error_no = -1
    organization = None

    try:
        organization = Organization.objects.get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == 'GET':
            form = OrganizationAddForm(instance=organization)

        if request.method == 'POST':
            form = OrganizationAddForm(request.POST or None, request.FILES, instance=organization)

            if form.is_valid():
                try:
                    organization = form.save(commit=True)
                    return redirect('admin.de_basic_info.organization')

                except Exception, exc:
                    pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, organization=organization, form=form, err=has_error,
             error_no=error_no, minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/organization_edit.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def organization_del(request, pk):
    try:
        obj = Organization.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_basic_info.organization")


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_type_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_form_message = False
    form_message = -1

    type_list = EntranceType.objects.all()

    if request.method == 'POST':
        form = EntranceTypeAddForm(request.POST or None)

        if form.is_valid():
            try:
                entrance_type = form.save(commit=True)

            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = EntranceTypeAddForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, types=type_list, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/entrance_type_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_type_del(request, pk):
    try:
        obj = EntranceType.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_basic_info.entrance_type")


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def examination_group_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_form_message = False
    form_message = -1

    e_group_list = ExaminationGroup.objects.all().prefetch_related('etype')

    if request.method == 'POST':
        form = ExaminationGroupAddForm(request.POST or None)

        if form.is_valid():
            try:
                examination_group = form.save(commit=True)

            except IntegrityError:
                form_message = 1
                has_form_message = True

    form = ExaminationGroupAddForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, egroups=e_group_list, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/examination_group_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def examination_group_del(request, pk):
    try:
        obj = ExaminationGroup.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_basic_info.examination_group")


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_set_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    e_set_list = EntranceSet.objects.all().prefetch_related('group', 'group__etype')

    d = dict(menul=menu_settings.menus, msel=menu_selected, esets=e_set_list, minnersel=inner_menu_selected, menuinner=entrance_menus)
    return render_to_response("admin/de_basic_info/entrance_set_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_set_add(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == 'GET':
        form = EntranceSetAddForm()
    if request.method == 'POST':
        form = EntranceSetAddForm(request.POST or None, request.FILES)

        if form.is_valid():
            try:
                entrance_set = form.save(commit=True)
                return redirect('admin.de_basic_info.entrance_set')
            except IntegrityError, exc:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/entrance_set_add.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_set_edit(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_error = False
    error_no = -1
    entrance_set = None

    try:
        entrance_set = EntranceSet.objects.get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == 'GET':
            form = EntranceSetEditForm(instance=entrance_set)
        if request.method == 'POST':
            form = EntranceSetEditForm(request.POST or None, request.FILES, instance=entrance_set)

            if form.is_valid():
                try:
                    entrance_set = form.save(commit=True)
                    return redirect('admin.de_basic_info.entrance_set')
                except Exception, exc:
                    print exc
                    pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, eset=entrance_set, err=has_error, error_no=error_no,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/entrance_set_edit.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_set_del(request, pk):
    try:
        obj = EntranceSet.objects.get(pk=pk)
        obj.delete()
    except Exception, exc:
        print exc
        pass

    return redirect("admin.de_basic_info.entrance_set")


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_lesson_type_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    etypes_list = EntranceType.objects.all()

    d = dict(menul=menu_settings.menus, msel=menu_selected, etypes=etypes_list,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    return render_to_response("admin/de_basic_info/entrance_lesson_type_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_lesson_detail_list(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    has_error = False
    error_no = -1
    entrance_type_record = None
    edetails = []

    try:
        entrance_type_record = EntranceType.objects.get(pk=pk)

        page = request.GET.get('page', 1)
        q = request.GET.get('q', '')
        q = q.strip()
        if len(q) == 0:
            edetails_list = EntranceLesson.objects.values('id', 'title', 'full_title').filter(entrance_type__id=pk)
        else:
            edetails_list = EntranceLesson.objects.values('id', 'title', 'full_title').filter(entrance_type__id=pk).filter(title__icontains=q)

        paginator = Paginator(edetails_list, 20)
        try:
            edetails = paginator.page(page)
        except PageNotAnInteger:
            edetails = paginator.page(1)
        except EmptyPage:
            edetails = paginator.page(paginator.num_pages)

    except:
        error_no = 1
        has_error = True

    d = dict(menul=menu_settings.menus, msel=menu_selected, edetails=edetails, etype=entrance_type_record,
             error_no=error_no, has_error=has_error, q=q,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    return render_to_response("admin/de_basic_info/entrance_lesson_detail_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_lesson_add(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1
    entrance_type_record = None
    form = None

    try:
        entrance_type_record = EntranceType.objects.get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == 'GET':
            form = EntranceLessonAddForm()
        elif request.method == 'POST':
            form = EntranceLessonAddForm(request.POST or None)

            if form.is_valid():
                try:
                    h = form.save(commit=False)
                    h.entrance_type = entrance_type_record
                    h.save()
                    return redirect("admin.de_basic_info.entrance_lesson.details", entrance_type_record.id)
                except IntegrityError:
                    has_form_message = True
                    form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, etype=entrance_type_record, error_no=error_no,
             has_error=has_error, form=form, has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/entrance_lesson_add.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_lesson_del(request, pk):
    try:
        obj = EntranceLesson.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_basic_info.entrance_lesson")


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_subset_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_form_message = False
    form_message = -1

    subsets_list = EntranceSubset.objects.all().prefetch_related('e_set')

    page = request.GET.get('page', 1)

    paginator = Paginator(subsets_list, 20)
    try:
        subsets = paginator.page(page)
    except PageNotAnInteger:
        subsets = paginator.page(1)
    except EmptyPage:
        subsets = paginator.page(paginator.num_pages)

    if request.method == 'GET':
        form = EntranceSubsetAddForm()
    if request.method == 'POST':
        form = EntranceSubsetAddForm(request.POST or None)

        if form.is_valid():
            try:
                entrance_subset = form.save(commit=True)
                return redirect('admin.de_basic_info.entrance_subset')
            except IntegrityError, exc:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, subsets=subsets,
             has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/entrance_subset_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def entrance_subset_del(request, pk):
    try:
        obj = EntranceSubset.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_basic_info.entrance_subset")


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def taskmessage_type_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_basic_info"

    form = None
    has_form_message = False
    form_message = -1

    task_message_type_list = TaskMessageType.objects.all()

    if request.method == 'POST':
        form = TaskMessageTypeAddForm(request.POST or None)

        if form.is_valid():
            try:
                task_m_type = form.save(commit=True)
            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = TaskMessageTypeAddForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, types=task_message_type_list, form=form,
             has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_basic_info/task_message_type_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_basic_info', raise_exception=True)
def taskmessage_type_del(request, pk):
    try:
        obj = TaskMessageType.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_basic_info.task_message_type")

