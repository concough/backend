# coding=utf-8
import uuid

from datetime import datetime

import pytz
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.utils.text import slugify
from gridfs import GridFS

from admin.Forms.DEHelpForms import HelpSectionsForm, HelpSectionLangAddForm, HelpSectionSubAddForm, \
    HelpSectionSubEditForm, HelpSectionSubDeviceAddForm, HelpSectionSubDeviceEditForm
from admin.Helpers import menu_settings, settings_menu_settings, contents_menu_settings
from main.Helpers.decorators import group_permission_required
from main.models_functions import connectToMongo


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_list(request):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1

    db = connectToMongo()

    if request.method == "GET":
        form = HelpSectionsForm()
    elif request.method == "POST":
        form = HelpSectionsForm(request.POST or None, files=request.FILES)


    if form.is_valid():
        unique_key = uuid.uuid4()
        title = form.cleaned_data["title"]
        color = form.cleaned_data['color']
        image = form.cleaned_data['image']

        section = db.help_sections.find_one({'title': title})
        if not section:
            fs_obj = None
            if image:
                fs = GridFS(db)
                fs_obj = fs.put(image, content_type=image.content_type)

            obj = {
                'unique_id': unique_key,
                'title': title,
                'color': color,
                'image': fs_obj,
                "created": datetime.now(tz=pytz.UTC),
                "updated": datetime.now(tz=pytz.UTC),
                "data": {}
            }

            db.help_sections.insert(obj)
            return redirect("admin.help_manage.sections")
        else:
            pass

    sections = db.help_sections.find({})

    d = dict(menul=menu_settings.menus, msel=menu_selected, help_sections=sections, form=form,
             minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
    return render_to_response("admin/de_helps/helps_sections_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_edit(request, unique_id):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1
    obj = None

    db = connectToMongo()

    try:
        obj = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
        if obj:
            if request.method == "GET":
                form = HelpSectionsForm(initial={'title': obj["title"], 'color': obj["color"]})
            elif request.method == "POST":
                form = HelpSectionsForm(request.POST or None, files=request.FILES,
                                        initial={'title': obj["title"], 'color': obj["color"]})

                if form.is_valid():
                    title = form.cleaned_data["title"]
                    color = form.cleaned_data['color']
                    image = form.cleaned_data['image']

                    fs_obj = None
                    if image:
                        fs = GridFS(db)
                        fs_obj = fs.put(image, content_type=image.content_type)

                    db.help_sections.update_one({'unique_id': uuid.UUID(unique_id)},
                                                {'$set': {"title": title,
                                                          "color": color,
                                                          "image": fs_obj,
                                                          "updated": datetime.now(tz=pytz.UTC),
                                                          }
                                                 })
                    return redirect("admin.help_manage.sections")
        else:
            return redirect("admin.help_manage.sections")

    except Exception, exc:
        has_form_message = True
        form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, section=obj, form=form, err=has_form_message,
             error_no=form_message,
             minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
    return render_to_response("admin/de_helps/helps_sections_edit.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_del(request, unique_id):
    db = connectToMongo()

    try:
        obj = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
        if obj:
            db.help_sections.delete_one({'unique_id': uuid.UUID(unique_id)})

    except Exception, exc:
        pass

    return redirect("admin.help_manage.sections")


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_list(request, unique_id):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1

    db = connectToMongo()
    section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})

    if section:
        if request.method == "GET":
            form = HelpSectionLangAddForm()
        elif request.method == "POST":
            form = HelpSectionLangAddForm(request.POST or None)

        if form.is_valid():
            title = form.cleaned_data["title"]
            lang = form.cleaned_data['lang']

            exist = False
            for key, item in section["data"]:
                if lang == key:
                    exist = True
                    break

            if not exist:
                obj = {
                    'title': title,
                    'slug': slugify(title, allow_unicode=True),
                    "subs": []
                }

                ket = "data.%s" % lang
                db.help_sections.update_one({'unique_id': uuid.UUID(unique_id)},
                                  {'$set': {ket: obj}
                                   })
            else:
                title_key = "data.%s.title" % lang
                slug_key = "data.%s.slug" % lang
                db.help_sections.update_one({'unique_id': uuid.UUID(unique_id)},
                                  {'$set': {title_key: title,
                                            slug_key: slugify(title, allow_unicode=True)}
                                   })

            return redirect("admin.help_manage.sections.langs.list", unique_id=unique_id)


    else:
        return redirect("admin.help_manage.sections")

    d = dict(menul=menu_settings.menus, msel=menu_selected, section=section, form=form,
             minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
    return render_to_response("admin/de_helps/helps_sections_lang_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_del(request, unique_id, lang):
    try:
        db = connectToMongo()
        section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})

        if section:
            title_key = "data.%s" % lang
            db.help_sections.update_one({'unique_id': uuid.UUID(unique_id)},
                              {'$unset': {title_key: ""}
                               })
    except:
        pass

    return redirect("admin.help_manage.sections.langs.list", unique_id=unique_id)


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_list(request, unique_id, lang):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    db = connectToMongo()
    section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
    subs = section["data"][lang]

    selected_sub = None
    q = request.GET.get('q', None)
    if q is not None:
        for s in subs["subs"]:
            if s["slug"] == q:
                selected_sub = s
                break

    d = dict(menul=menu_settings.menus, msel=menu_selected, section=section, subs=subs, lang=lang,
             selected_sub=selected_sub, slug=q,
             minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
    return render_to_response("admin/de_helps/helps_sections_subs.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_add(request, unique_id, lang):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1

    db = connectToMongo()
    section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
    if section:
        if request.method == "GET":
            form = HelpSectionSubAddForm()
        elif request.method == "POST":
            form = HelpSectionSubAddForm(request.POST or None)


            if form.is_valid():
                exist = False
                for sub in section["data"][lang]["subs"]:
                    if sub["slug"] == slugify(form.cleaned_data['title'], allow_unicode=True):
                        exist = True
                        break

                if not exist:
                    obj = {
                        'unique_id': uuid.uuid4(),
                        'title': form.cleaned_data['title'],
                        'slug': slugify(form.cleaned_data['title'], allow_unicode=True),
                        'order': form.cleaned_data['order'],
                        'description': form.cleaned_data['description'],
                        'created': datetime.now(tz=pytz.UTC),
                        'updated': datetime.now(tz=pytz.UTC),
                        'devices': {},
                        'available': False
                    }
                    title_key = "data.%s.subs" % lang
                    db.help_sections.update_one({'unique_id': uuid.UUID(unique_id)},
                                                {"$addToSet": {
                                                    title_key: obj
                                                }, '$set': {
                                                        'updated': datetime.now(tz=pytz.UTC)
                                                    }
                                                })

                return redirect("admin.help_manage.sections.langs.subs", unique_id=unique_id, lang=lang)

    d = dict(menul=menu_settings.menus, msel=menu_selected, section=section, form=form, lang=lang,
             minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
    return render_to_response("admin/de_helps/helps_sections_subs_add.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_edit(request, unique_id, lang, sub_unique_id):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1

    section = None
    selected_sub = None

    db = connectToMongo()
    section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
    if section:
        # get initial data
        description_temp = ""
        order_temp = 1
        for s in section["data"][lang]["subs"]:
            if s["unique_id"] == uuid.UUID(sub_unique_id):
                selected_sub = s
                description_temp = s["description"]
                order_temp = s["order"]
                break

        if selected_sub:
            if request.method == "GET":
                form = HelpSectionSubEditForm(initial={'description': description_temp, 'order': order_temp})
            elif request.method == "POST":
                form = HelpSectionSubEditForm(request.POST or None, initial={'description': description_temp, 'order': order_temp})

                if form.is_valid():
                    unique_key = "data.%s.subs.unique_id" % lang
                    desc_key = "data.%s.subs.$.description" % lang
                    order_key = "data.%s.subs.$.order" % lang
                    db.help_sections.update_one({'unique_id': uuid.UUID(unique_id),
                                                 unique_key: uuid.UUID(sub_unique_id)},
                                                {"$set": {
                                                    desc_key: form.cleaned_data["description"],
                                                    order_key: form.cleaned_data["order"],
                                                    'updated': datetime.now(tz=pytz.UTC)
                                                }})

                    return redirect(reverse("admin.help_manage.sections.langs.subs", kwargs={'unique_id':unique_id, 'lang':lang}) + "?q=" + selected_sub["slug"])

    d = dict(menul=menu_settings.menus, msel=menu_selected, section=section, form=form, lang=lang, selected_sub=selected_sub,
             minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
    return render_to_response("admin/de_helps/helps_sections_subs_edit.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_del(request, unique_id, lang, sub_unique_id):
    try:
        db = connectToMongo()
        section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
        for su in section["data"][lang]["subs"]:
            if su["unique_id"] == uuid.UUID(sub_unique_id):
                key = "data.%s.subs.unique_id" % lang
                key_data = "data.%s.subs" % lang

                db.help_sections.update_one({'unique_id': uuid.UUID(unique_id)},
                                            {
                                                '$pull': {
                                                    key_data: {'unique_id': uuid.UUID(sub_unique_id)}
                                                },
                                                '$set': {
                                                    'updated': datetime.now(tz=pytz.UTC)
                                                }
                                            }
                                            )
    except:
        pass

    return redirect("admin.help_manage.sections.langs.subs", unique_id=unique_id, lang=lang)


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_available(request, unique_id, lang, sub_unique_id):
    try:
        db = connectToMongo()
        section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
        for su in section["data"][lang]["subs"]:
            if su["unique_id"] == uuid.UUID(sub_unique_id):
                key = "data.%s.subs.unique_id" % lang
                avail_key = "data.%s.subs.$.available" % lang
                updated_key = "data.%s.subs.$.updated" % lang
                db.help_sections.update_one({'unique_id': uuid.UUID(unique_id),
                                             key: uuid.UUID(sub_unique_id)},
                                            {'$set': {avail_key: True,
                                                      updated_key: datetime.now(tz=pytz.UTC),
                                                      'updated': datetime.now(tz=pytz.UTC)
                                                      }}
                                            )
    except:
        pass

    return redirect("admin.help_manage.sections.langs.subs", unique_id=unique_id, lang=lang)


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_unavailable(request, unique_id, lang, sub_unique_id):
    try:
        db = connectToMongo()
        section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
        if section:
            for su in section["data"][lang]["subs"]:
                if su["unique_id"] == uuid.UUID(sub_unique_id):
                    key = "data.%s.subs.unique_id" % lang
                    avail_key = "data.%s.subs.$.available" % lang
                    updated_key = "data.%s.subs.$.updated" % lang
                    db.help_sections.update_one({'unique_id': uuid.UUID(unique_id),
                                                 key: uuid.UUID(sub_unique_id)},
                                                {'$set': {avail_key: False,
                                                          updated_key: datetime.now(tz=pytz.UTC),
                                                          'updated': datetime.now(tz=pytz.UTC)
                                                          }}
                                                )
                    break
    except:
        pass

    return redirect("admin.help_manage.sections.langs.subs", unique_id=unique_id, lang=lang)


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_device_add(request, unique_id, lang, sub_unique_id):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1

    section = None
    selected_sub = None

    db = connectToMongo()
    section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
    if section:
        for sub in section["data"][lang]["subs"]:
            if sub["unique_id"] == uuid.UUID(sub_unique_id):
                selected_sub = sub

        if selected_sub:
            if request.method == "GET":
                form = HelpSectionSubDeviceAddForm()
            elif request.method == "POST":
                form = HelpSectionSubDeviceAddForm(request.POST or None)


                if form.is_valid():
                    exist = False
                    if form.cleaned_data['device'] in selected_sub['devices'].keys():
                        exist = True

                    if not exist:
                        obj = {
                            'description': form.cleaned_data['description'],
                            'created': datetime.now(tz=pytz.UTC),
                            'updated': datetime.now(tz=pytz.UTC),
                            'is_helpful_yes': 0,
                            'is_helpful_no': 0
                        }
                        sub_key = "data.%s.subs.unique_id" % lang
                        device_key = "data.%s.subs.$.devices.%s" % (lang, form.cleaned_data['device'])
                        update_key2 = "data.%s.subs.$.updated" % lang

                        db.help_sections.update_one({'unique_id': uuid.UUID(unique_id),
                                                     sub_key: uuid.UUID(sub_unique_id)},
                                                    {"$set": {
                                                        device_key: obj,
                                                        update_key2: datetime.now(tz=pytz.UTC)
                                                    }})

                        return redirect(reverse("admin.help_manage.sections.langs.subs",
                                                kwargs={'unique_id': unique_id, 'lang': lang}) + "?q=" + selected_sub[
                                            "slug"])

        d = dict(menul=menu_settings.menus, msel=menu_selected, section=section, form=form, lang=lang, selected_sub=selected_sub,
                 minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
        return render_to_response("admin/de_helps/helps_sections_subs_device_add.html", d,
                                  context_instance=RequestContext(request))

    return redirect(reverse("admin.help_manage.sections.langs.subs",
                                                kwargs={'unique_id': unique_id, 'lang': lang}))

@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_device_edit(request, unique_id, lang, sub_unique_id, device):
    menu_selected = "contents"
    inner_menu_selected = "settings_help"

    form = None
    has_form_message = False
    form_message = -1

    section = None
    selected_sub = None

    db = connectToMongo()
    section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
    if section:
        description_temp = ""
        for s in section["data"][lang]["subs"]:
            if s["unique_id"] == uuid.UUID(sub_unique_id):
                selected_sub = s
                for dev in s["devices"].keys():
                    if dev == device:
                        description_temp = s["devices"][dev]["description"]
                break

        if selected_sub:
            if request.method == "GET":
                form = HelpSectionSubDeviceEditForm(initial={'description': description_temp})
            elif request.method == "POST":
                form = HelpSectionSubDeviceEditForm(request.POST or None, initial={'description': description_temp})

                if form.is_valid():
                    sub_key = "data.%s.subs.unique_id" % lang
                    device_key = "data.%s.subs.$.devices.%s.description" % (lang, device)
                    update_key = "data.%s.subs.$.devices.%s.updated" % (lang, device)
                    update_key2 = "data.%s.subs.$.updated" % lang

                    db.help_sections.update_one({'unique_id': uuid.UUID(unique_id),
                                                 sub_key: uuid.UUID(sub_unique_id)},
                                                {"$set": {
                                                    device_key: form.cleaned_data["description"],
                                                    update_key: datetime.now(tz=pytz.UTC),
                                                    update_key2: datetime.now(tz=pytz.UTC)
                                                }})

                    return redirect(reverse("admin.help_manage.sections.langs.subs",
                                            kwargs={'unique_id': unique_id, 'lang': lang}) + "?q=" + selected_sub[
                                        "slug"])
            d = dict(menul=menu_settings.menus, msel=menu_selected, section=section, form=form, lang=lang,
                     selected_sub=selected_sub, device=device,
                     minnersel=inner_menu_selected, menuinner=contents_menu_settings.contents_menus)
            return render_to_response("admin/de_helps/helps_sections_subs_device_edit.html", d,
                                  context_instance=RequestContext(request))
        else:
            pass

    return redirect(reverse("admin.help_manage.sections.langs.subs",
                        kwargs={'unique_id': unique_id, 'lang': lang}))


@login_required
@group_permission_required('main.de_helps', raise_exception=True)
def helps_sections_lang_subs_device_del(request, unique_id, lang, sub_unique_id, device):
    try:
        db = connectToMongo()
        section = db.help_sections.find_one({'unique_id': uuid.UUID(unique_id)})
        if section:
            for s in section["data"][lang]["subs"]:
                if s["unique_id"] == uuid.UUID(sub_unique_id):
                    for dev in s["devices"].keys():
                        if dev == device:
                            sub_key = "data.%s.subs.unique_id" % lang
                            device_key = "data.%s.subs.$.devices.%s" % (lang, device)
                            db.help_sections.update_one({'unique_id': uuid.UUID(unique_id),
                                                         sub_key: uuid.UUID(sub_unique_id)},
                                                        {
                                                            '$unset': {
                                                                device_key: ""
                                                            }
                                                        }
                                                        )
                            return redirect(reverse("admin.help_manage.sections.langs.subs",
                                            kwargs={'unique_id': unique_id, 'lang': lang}) + "?q=" + s[
                                        "slug"])

    except:
        pass

    return redirect("admin.help_manage.sections.langs.subs", unique_id=unique_id, lang=lang)

