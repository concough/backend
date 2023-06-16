from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.context_processors import csrf

from admin.Forms.DECostsManageForms import EntranceSaleDataAddForm, EntranceTagsSaleDataAddForm, ConcoughGiftCardAddForm
from admin.Helpers import menu_settings
from admin.Helpers.costs_menu_settings import costs_menus
from main.Helpers.decorators import group_permission_required
from main.Helpers.model_static_values import ENTRANCE_TAG_SALE_Q_COUNT
from main.models import EntranceSaleData, EntranceTagSaleData, ConcoughGiftCard


@login_required
@group_permission_required('main.de_costs_manage', raise_exception=True)
def entrance_sale_data_list(request):
    menu_selected = "costs"
    inner_menu_selected = "entrance_costs"

    has_form_message = False
    form_message = -1

    sale_data_list = EntranceSaleData.objects.all()

    if request.method == 'POST':
        form = EntranceSaleDataAddForm(request.POST or None)

        if form.is_valid():
            try:
                etype = form.cleaned_data["entrance_type"]
                year = form.cleaned_data["year"]
                month = form.cleaned_data["month"]

                obj, create = EntranceSaleData.objects.update_or_create(entrance_type=etype, year=year, month=month,
                                                                        defaults={'cost': form.cleaned_data["cost"],
                                                                                  'cost_bon': form.cleaned_data["cost_bon"]})

                #record = form.save(commit=True)

            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = EntranceSaleDataAddForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, sales=sale_data_list, form=form,
             has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=costs_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_costs/entrance_sale_data_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_costs_manage', raise_exception=True)
def entrance_tags_sale_data_list(request):
    menu_selected = "costs"
    inner_menu_selected = "entrance_tags_costs"

    has_form_message = False
    form_message = -1

    sale_data_list = EntranceTagSaleData.objects.all()

    if request.method == 'POST':
        form = EntranceTagsSaleDataAddForm(request.POST or None)

        if form.is_valid():
            try:
                etype = form.cleaned_data["entrance_type"]
                year = form.cleaned_data["year"]
                month = form.cleaned_data["month"]

                obj, create = EntranceTagSaleData.objects.update_or_create(entrance_type=etype, year=year, month=month,
                                                                        defaults={'cost': form.cleaned_data["cost"],
                                                                                  'q_count': ENTRANCE_TAG_SALE_Q_COUNT})

            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = EntranceTagsSaleDataAddForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, sales=sale_data_list, form=form,
             has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=costs_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_costs/entrance_tags_sale_data_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_costs_manage', raise_exception=True)
def concough_gift_card_list(request):
    menu_selected = "costs"
    inner_menu_selected = "gift_cards"

    has_form_message = False
    form_message = -1

    gift_card_list = ConcoughGiftCard.objects.all()

    if request.method == 'POST':
        form = ConcoughGiftCardAddForm(request.POST or None)

        if form.is_valid():
            try:
                etype = form.cleaned_data["entrance_type"]
                year = form.cleaned_data["year"]
                month = form.cleaned_data["month"]

                obj, create = EntranceSaleData.objects.update_or_create(entrance_type=etype, year=year, month=month,
                                                                        defaults={'cost': form.cleaned_data["cost"],
                                                                                  'cost_bon': form.cleaned_data[
                                                                                      "cost_bon"]})

                # record = form.save(commit=True)

            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = ConcoughGiftCardAddForm()

    d = dict(menul=menu_settings.menus, msel=menu_selected, cards=gift_card_list, form=form,
             has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=costs_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_costs/entrance_sale_data_list.html", d,
                              context_instance=RequestContext(request))