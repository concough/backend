from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf
from admin.Forms.DEEntranceFactorsForms import EntranceFactorAddForm
from admin.Helpers import menu_settings
from admin.Helpers.entrance_menu_settings import entrance_menus
from main.Helpers.decorators import group_permission_required
from main.models import Entrance, EntranceSubsetFactor

__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_entrance_factors', raise_exception=True)
def entrance_factor_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrancefactors"

    page = request.GET.get('page', 1)
    entrance_list = Entrance.objects.all().prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                            'entrance_set__group').order_by('year', 'month')

    paginator = Paginator(entrance_list, 20)
    try:
        entrances = paginator.page(page)
    except PageNotAnInteger:
        entrances = paginator.page(1)
    except EmptyPage:
        entrances = paginator.page(paginator.num_pages)

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrances=entrances,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    return render_to_response("admin/de_entrance_factors/entrance_factors_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_factors', raise_exception=True)
def entrance_factor_view(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrancefactors"

    form = None
    has_error = False
    error_no = -1
    form_message = -1
    has_form_message = False
    factors = {}
    entrance = None

    try:
        entrance = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                     'entrance_set__group').get(pk=pk)
    except Exception, exc:
        has_error = True
        error_no = 1

    if not has_error:
        factors_list = EntranceSubsetFactor.objects.filter(entrance__id=entrance.id).prefetch_related('subset',
                                                                                                      'lesson') \
            .order_by('subset', 'lesson')

        for item in factors_list:
            if not factors.has_key(item.subset.title):
                factors[item.subset.title] = []

            factors[item.subset.title].append(item)

        if request.method == 'GET':
            form = EntranceFactorAddForm(ebd_id=entrance.id, eset=entrance.entrance_set)
        elif request.method == 'POST':
            form = EntranceFactorAddForm(ebd_id=entrance.id, eset=entrance.entrance_set, data=request.POST or None)

            if form.is_valid():
                try:
                    record = form.save(commit=False)
                    record.entrance = entrance
                    record.save()
                    return redirect('admin.de_entrance_factors.view', pk=entrance.id)

                except IntegrityError:
                    has_form_message = True
                    form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, has_error=has_error,
             error_no=error_no, factors=factors, entrance=entrance, has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance_factors/entrance_factors_detail.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_factors', raise_exception=True)
def entrance_factor_del(request, pk1, pk2):
    factors = EntranceSubsetFactor.objects.filter(subset__id=pk2)
    factors.delete()

    return redirect('admin.de_entrance_factors.view', pk=pk1)