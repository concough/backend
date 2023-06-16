from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf

from admin.Forms.DEGenaralForms import SearchForm
from admin.Forms.SettingsForms import UserFinancialAddForm, UserFinancialEditForm
from admin.Forms.UserManagementForms import UserAddForm, UserEditForm, UserCheckerStateChangeForm
from admin.Helpers import menu_settings
from admin.Helpers.settings_menu_settings import settings_menus
from main.Helpers.decorators import group_permission_required
from main.models import UserFinanialInformation, UserCheckerState
from main.models_functions import connectToMongo

__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_settings.usermgmt', raise_exception=True)
def users_list(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    users = []

    if request.method == "GET":
        # show all users in groups ('master_operator', 'editor', 'picture_creator', 'check_in')
        users = User.objects.filter(groups__name__in=('master_operator', 'editor', 'picture_creator', 'check_in', 'reporter'))\
            .prefetch_related('groups')
    elif request.method == "POST":
        form = SearchForm(request.POST or None)
        if form.is_valid():
            q = form.cleaned_data["q"].strip()

            if len(q) > 0:
                users = User.objects.filter(username__startswith=q).prefetch_related('groups')

    d = dict(menul=menu_settings.menus, msel=menu_selected, users=users, minnersel=inner_menu_selected, menuinner=settings_menus)
    return render_to_response("admin/de_settings/users_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_settings.usermgmt', raise_exception=True)
def users_add(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == 'GET':
        form = UserAddForm()
    elif request.method == 'POST':
        form = UserAddForm(request.POST or None)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            is_staff = form.cleaned_data['is_staff']
            groups = form.cleaned_data['temp_groups']
            try:
                created_user = User.objects.create_user(username, email, password)
                created_user.first_name = first_name
                created_user.last_name = last_name
                created_user.is_staff = is_staff
                created_user.is_active = True
                # saving groups
                created_user.groups = groups
                created_user.save()

                if 'check_in' in groups:
                    print "Checker"

                    check_state = UserCheckerState()
                    check_state.user = created_user
                    check_state.state = "SINGLE"

                    check_state.save()

                return redirect('admin.de_settings.user_mgmt')

            except IntegrityError, exc:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=settings_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_settings/users_add.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_settings.usermgmt', raise_exception=True)
def users_edit(request, pk):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    form = None
    has_form_message = False
    form_message = -1
    user = None

    try:
        user = User.objects.get(pk=pk)

        if request.method == 'GET':
            form = UserEditForm(instance=user)
        elif request.method == 'POST':
            form = UserEditForm(instance=user, data=request.POST or None)

            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                is_staff = form.cleaned_data['is_staff']
                groups = form.cleaned_data['temp_groups']

                user.first_name = first_name
                user.last_name = last_name
                user.is_staff = is_staff
                # saving groups
                user.groups = groups
                user.save()

                if 'check_in' not in groups:
                    checker_state = UserCheckerState.objects.filter(user=user)
                    if len(checker_state) > 0:
                        checker_state.delete()

                return redirect('admin.de_settings.user_mgmt')

    except IntegrityError, exc:
        has_form_message = True
        form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, user1=user,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=settings_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_settings/users_edit.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_settings.usermgmt', raise_exception=True)
def users_deactivate(request, pk):
    try:
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.save()
    except:
        pass

    return redirect('admin.de_settings.user_mgmt')


@login_required
@group_permission_required('main.de_settings.usermgmt', raise_exception=True)
def users_activate(request, pk):
    try:
        user = User.objects.get(pk=pk)
        user.is_active = True
        user.save()
    except:
        pass

    return redirect('admin.de_settings.user_mgmt')


@login_required
@group_permission_required('main.de_settings.usermgmt.financial', raise_exception=True)
def users_financial_list(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    # show all users in groups ('master_operator', 'editor', 'picture_creator')
    users_finance_list = UserFinanialInformation.objects.all().prefetch_related('user')

    d = dict(menul=menu_settings.menus, msel=menu_selected, uf=users_finance_list, minnersel=inner_menu_selected,
             menuinner=settings_menus)
    return render_to_response("admin/de_settings/users_financial_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_settings.usermgmt.financial', raise_exception=True)
def users_financial_add(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == 'GET':
        form = UserFinancialAddForm()
    elif request.method == 'POST':
        form = UserFinancialAddForm(request.POST or None)

        if form.is_valid():
            try:
                form.save()
                return redirect('admin.de_settings.user_mgmt.financial')

            except IntegrityError, exc:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected,
             menuinner=settings_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_settings/users_financial_add.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_settings.usermgmt.financial', raise_exception=True)
def users_financial_edit(request, pk):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    form = None
    has_error = False
    error_no = -1
    userf = None

    try:
        userf = UserFinanialInformation.objects.get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:

        if request.method == 'GET':
            form = UserFinancialEditForm(instance=userf)
        elif request.method == 'POST':
            form = UserFinancialEditForm(request.POST or None, instance=userf)

            if form.is_valid():
                try:
                    form.save()

                    db = connectToMongo()
                    job_finance = db.job_finance.update_one({'user_id': userf.user.id}, {
                        '$set': {
                            'finance_detail.shaba': form.cleaned_data["bank_shaba"],
                            'finance_detail.bank_name': form.cleaned_data["bank_name"]
                        }
                    })

                    return redirect('admin.de_settings.user_mgmt.financial')

                except IntegrityError, exc:
                    pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form,
             has_form_message=has_error, error_no=error_no, minnersel=inner_menu_selected,
             menuinner=settings_menus, userf=userf)
    d.update(csrf(request))
    return render_to_response("admin/de_settings/users_financial_edit.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_settings.usermgmt.financial', raise_exception=True)
def users_financial_del(request, pk):
    try:
        obj = UserFinanialInformation.objects.get(pk=pk)
        obj.delete()
    except:
        pass

    return redirect("admin.de_settings.user_mgmt.financial")


@login_required
@group_permission_required('main.de_settings.usermgmt', raise_exception=True)
def users_checkers_state_list(request):
    menu_selected = "settings"
    inner_menu_selected = "settings_user_mgmt"

    form = None
    has_form_message = False
    form_message = -1

    checkers_list = UserCheckerState.objects.all().prefetch_related('user')

    if request.method == 'POST':
        form = UserCheckerStateChangeForm(request.POST or None)

        if form.is_valid():
            try:
                user = form.cleaned_data['user']
                state = form.cleaned_data['state']

                obj, created = UserCheckerState.objects.update_or_create(user=user, defaults={
                    'state': state
                })

                return redirect('admin.de_settings.user_mgmt.checker_state')

            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = UserCheckerStateChangeForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, checkers_list=checkers_list, form=form,
             has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected, menuinner=settings_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_settings/users_checkers_state_list.html", d, context_instance=RequestContext(request))