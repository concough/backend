from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template.context_processors import csrf

from admin.Forms.DEContentForms import ContentQuotesCategoryAddForm, ContentQuotesAddForm, ContentQuotesEditForm
from admin.Helpers import menu_settings
from admin.Helpers import contents_menu_settings
from main.Helpers.decorators import group_permission_required
from main.models import ContentQuotesCategory, ContentQuote


@login_required
@group_permission_required('main.de_content_provide', raise_exception=True)
def content_dashboard(request):
    menu_selected = "contents"
    inner_menu_selected = "dashboard"

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=contents_menu_settings.contents_menus)
    return render_to_response('admin/de_contents/dashboard.html', d, context_instance=RequestContext(request))


# list quotes
@login_required
@group_permission_required('main.de_content_quotes', raise_exception=True)
def content_quotes_category_list(request):
    menu_selected = "contents"
    inner_menu_selected = "content_quotes"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == "POST":
        form = ContentQuotesCategoryAddForm(request.POST or None)
        if form.is_valid():
            try:
                qcat = form.save(commit=True)

                return redirect('admin.content_mgm.quotes.categories')
            except IntegrityError:
                has_form_message = True
                form_message = 1

    form = ContentQuotesCategoryAddForm()

    categories = ContentQuotesCategory.objects.all()
    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=contents_menu_settings.contents_menus, categories=categories, form=form,
             has_form_message=has_form_message, form_message=form_message,)
    return render_to_response('admin/de_contents/quotes_category_list.html', d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_content_quotes', raise_exception=True)
def content_quotes_category_del(request, pk):
    try:
        cat = ContentQuotesCategory.objects.get(pk=pk)
        cat.delete()
    except:
        pass

    return redirect('admin.content_mgm.quotes.categories')


# list quotes
@login_required
@group_permission_required('main.de_content_quotes', raise_exception=True)
def content_quotes_list(request):
    menu_selected = "contents"
    inner_menu_selected = "content_quotes"

    page = request.GET.get('page', 1)
    code = request.GET.get('code', "all")
    user_group_names = request.user.groups.all()

    if 'master_operator' in [grp.name for grp in user_group_names] or 'administrator' in [grp.name for grp in
                                                                                          user_group_names]:
        if code == "all":
            quotes_list = ContentQuote.objects.all().order_by('app_show_count', '-updated')
        else:
            quotes_list = ContentQuote.objects.filter(category__code=code).order_by('app_show_count', '-updated')
    else:
        if code == "all":
            quotes_list = ContentQuote.objects.filter(creator=request.user).order_by('app_show_count', '-updated')
        else:
            quotes_list = ContentQuote.objects.filter(creator=request.user, category__code=code).order_by('app_show_count', '-updated')

    paginator = Paginator(quotes_list, 10)
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        quotes = paginator.page(1)
    except EmptyPage:
        quotes = paginator.page(paginator.num_pages)

    categories = ContentQuotesCategory.objects.all()
    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=contents_menu_settings.contents_menus, quotes=quotes, categories=categories, selected_code=code)
    return render_to_response('admin/de_contents/quotes_list.html', d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_content_quotes', raise_exception=True)
def content_quotes_add(request):
    menu_selected = "contents"
    inner_menu_selected = "content_quotes"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == "GET":
        form = ContentQuotesAddForm()
    elif request.method == "POST":
        form = ContentQuotesAddForm(request.POST or None, files=request.FILES)

        if form.is_valid():
            try:
                tcategories = form.cleaned_data['temp_category']

                quote = form.save(commit=False)
                quote.creator = request.user
                quote.save()

                for cat in tcategories:
                    quote.category.add(cat)

                return redirect('admin.content_mgm.quotes')

            except Exception, exc:
                print exc
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=contents_menu_settings.contents_menus, form=form, has_form_message=has_form_message,
             form_message=form_message,)
    d.update(csrf(request))
    return render_to_response('admin/de_contents/quotes_add.html', d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_content_quotes', raise_exception=True)
def content_quotes_edit(request, pk):
    menu_selected = "contents"
    inner_menu_selected = "content_quotes"

    form = None
    has_form_message = False
    form_message = -1
    quote = None

    try:
        quote = ContentQuote.objects.get(pk=pk)
    except:
        form_message = 2
        has_form_message = True

    if not has_form_message:
        if request.method == "GET":
            form = ContentQuotesEditForm(instance=quote)

        elif request.method == "POST":
            form = ContentQuotesEditForm(request.POST or None, instance=quote)

            if form.is_valid():
                try:
                    tcategories = form.cleaned_data['temp_category']
                    quote = form.save(commit=True)

                    for cat in tcategories:
                        quote.category.add(cat)

                    return redirect('admin.content_mgm.quotes')
                except:
                    form_message = 1
                    has_form_message = True

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=contents_menu_settings.contents_menus, form=form, form_message=form_message,
             has_form_message=has_form_message, quote=quote)
    d.update(csrf(request))
    return render_to_response('admin/de_contents/quotes_edit.html', d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_content_quotes.manage', raise_exception=True)
def content_quotes_del(request, pk):
    try:
        q = ContentQuote.objects.get(pk=pk)
        q.delete()

    except Exception, exc:
        print exc

    return redirect('admin.content_mgm.quotes')


@login_required
@group_permission_required('main.de_content_quotes.manage', raise_exception=True)
def content_quotes_publish_app(request, pk):
    return redirect('admin.content_mgm.quotes')


@login_required
@group_permission_required('main.de_content_quotes.manage', raise_exception=True)
def content_quotes_publish_blog(request, pk):
    return redirect('admin.content_mgm.quotes')
