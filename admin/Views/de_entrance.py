import json
import os
import copy, shutil
import uuid
import cachalot
import time
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.template.context_processors import csrf
from django.utils.baseconv import base64
from django.utils.datetime_safe import datetime
import lz4tools
import pytz
from gridfs import GridFS

from admin.Forms.DEEntranceForms import EntranceAddForm, EntranceBookletAddForm, EntranceBookletDetailAddForm, \
    EntranceQuestionEditForm, EntranceQuestionPictureAddForm, EntranceExtraDataAddForm, EntranceQuestionEditByFileForm, \
    EntranceQuestionPictureAddForm2, EntranceJobAssignForm, EntranceMultiAddForm, EntranceQuestionTagAddForm, \
    EntranceQuestionTagFileForm
from admin.Helpers import menu_settings
from admin.Helpers.entrance_menu_settings import entrance_menus
from digikunkor import settings
from main.Helpers.decorators import group_permission_required
from main.Helpers.model_static_values import CONCOUGH_LOG_TYPES, CONCOUGH_LOG_TYPES_2
from main.models import Entrance, EntranceBooklet, EntranceBookletDetail, EntranceLesson, EntranceQuestion, \
    EntranceQuestionImages, EntranceLogType, EntranceLog, EntrancePackage, EntrancePackageType, ConcoughActivity, \
    EntranceMulti, EntranceType, ExaminationGroup, EntranceSet, Tags, EntranceLessonTagPackage, EntranceTagSaleData
from main.models_functions import connectToMongo
from main.utils import create_concough_activity, create_product_statistic

__author__ = 'abolfazl'


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    page = request.GET.get('page', 1)
    entrance_list = Entrance.objects.all() \
        .prefetch_related('organization', 'entrance_type', 'entrance_set', 'entrance_set__group') \
        .order_by('published', 'is_editing', '-last_update')

    paginator = Paginator(entrance_list, 20)
    try:
        entrances = paginator.page(page)
    except PageNotAnInteger:
        entrances = paginator.page(1)
    except EmptyPage:
        entrances = paginator.page(paginator.num_pages)

    ent_ids = []
    for ent in entrances:
        ent_ids.append(ent.unique_key)

    jobs = {}
    try:
        db = connectToMongo()
        job_list = db.job.find({'job_relate_uniqueid': {'$in': ent_ids}},
                               {'job_relate_uniqueid': 1, 'status': 1, 'job_owner': 1})

        for l in job_list:
            print l
            jobs[l['job_relate_uniqueid'].hex] = {}
            jobs[l['job_relate_uniqueid'].hex]['status'] = l['status']
            if 'job_owner' in l:
                jobs[l['job_relate_uniqueid'].hex]['job_owner'] = l['job_owner']
    except:
        pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrances=entrances, minnersel=inner_menu_selected,
             menuinner=entrance_menus, jobs=jobs)
    return render_to_response("admin/de_entrance/entrance_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_jobs_finished_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1
    per_page = 20

    jobs = None
    entrance_ids = {}
    try:
        db = connectToMongo()
        jobs = db.job.find({'$and': [{'status': "FINISHED"}, {'job_type': "ENTRANCE"}]}).sort(
            [('updated', -1)]).skip((page - 1) * per_page).limit(per_page)

        uids = [job["job_relate_uniqueid"] for job in jobs.clone()]
        entrance_list = Entrance.objects.filter(unique_key__in=uids)

        for entrance in entrance_list:
            entrance_ids[entrance.unique_key.hex] = entrance.id

    except:
        pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=entrance_menus, jobs=jobs, entrance_ids=entrance_ids, page=page + 1)
    return render_to_response("admin/de_entrance/entrance_job_finished_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_del(request, pk):
    try:
        entrance = Entrance.objects.get(pk=pk)
        entrance.delete()
    except:
        pass

    return redirect('admin.de_entrance')


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_add(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    has_form_message = False
    form_message = -1

    if request.method == "GET":
        form = EntranceAddForm()
    elif request.method == "POST":
        form = EntranceAddForm(request.POST or None)

        if form.is_valid():
            try:
                entrance = form.save()
                return redirect('admin.de_entrance.booklets', pk=entrance.id)
            except IntegrityError:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, form=form, has_form_message=has_form_message,
             form_message=form_message, minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_add.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_booklets_list(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    has_error = False
    error_no = -1

    entrance = None
    booklets = []
    entrance_extra_data = None

    job_assign_form = EntranceJobAssignForm()

    try:
        entrance = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                     'entrance_set__group').get(pk=pk)
    except Exception, exc:
        # print exc
        has_error = True
        error_no = 1

    if not has_error:
        booklets = EntranceBooklet.objects.filter(entrance=entrance).prefetch_related('bookletdetails',
                                                                                      'bookletdetails__lesson').order_by(
            'order')
        try:
            entrance_extra_data = json.loads(entrance.extra_data, encoding="utf-8")
        except:
            pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrance=entrance, booklets=booklets,
             has_error=has_error, error_no=error_no, edata=entrance_extra_data,
             minnersel=inner_menu_selected, menuinner=entrance_menus, job_assign_form=job_assign_form)
    return render_to_response("admin/de_entrance/entrance_booklets_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_booklet_add(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1
    entrance = None

    try:
        entrance = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                     'entrance_set__group').get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        # create form
        if request.method == "GET":
            form = EntranceBookletAddForm()
        elif request.method == "POST":
            form = EntranceBookletAddForm(request.POST or None)

            if form.is_valid():
                try:
                    ebooklet = form.save(commit=False)
                    ebooklet.entrance = entrance
                    ebooklet.save()
                    return redirect("admin.de_entrance.booklets", pk=entrance.id)

                except IntegrityError:
                    has_form_message = True
                    form_message = 2

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrance=entrance, has_error=has_error, error_no=error_no,
             form=form, has_form_message=has_form_message, form_message=form_message, minnersel=inner_menu_selected,
             menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_booklets_add.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_booklet_del(request, pk):
    id = 0
    try:
        entrance_booklet = EntranceBooklet.objects.get(pk=pk)
        id = entrance_booklet.entrance.id
        entrance_booklet.delete()
    except:
        pass

    if id > 0:
        return redirect('admin.de_entrance.booklets', pk=id)
    else:
        return redirect('admin.de_entrance')


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_booklet_detail_add(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1
    entrance_booklet = None

    try:
        entrance_booklet = EntranceBooklet.objects \
            .prefetch_related('entrance', 'entrance__entrance_type', 'entrance__organization', 'entrance__entrance_set') \
            .get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == 'GET':
            form = EntranceBookletDetailAddForm()
        elif request.method == 'POST':
            form = EntranceBookletDetailAddForm(request.POST or None)

            if form.is_valid():
                q_from = form.cleaned_data['q_from']
                q_to = form.cleaned_data['q_to']

                try:
                    booklet_detail = form.save(commit=False)
                    booklet_detail.booklet = entrance_booklet
                    booklet_detail.q_count = q_to - q_from + 1
                    booklet_detail.save()

                    return redirect('admin.de_entrance.booklets', pk=entrance_booklet.entrance.id)

                except IntegrityError:
                    has_form_message = True
                    form_message = 1

        form.fields['lesson'].queryset = EntranceLesson.objects.filter(
            entrance_type=entrance_booklet.entrance.entrance_type)

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrance_booklet=entrance_booklet, has_error=has_error,
             error_no=error_no, form=form, has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_booklets_detail_add.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_booklet_detail_del(request, pk):
    id = 0
    try:
        entrance_booklet_det = EntranceBookletDetail.objects.get(pk=pk)
        id = entrance_booklet_det.booklet.entrance.id
        entrance_booklet_det.delete()
    except:
        pass

    if id > 0:
        return redirect('admin.de_entrance.booklets', pk=id)
    else:
        return redirect('admin.de_entrance')


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_list(request, pk):
    # pk = EntranceBookletDetail__id
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1

    booklet_detail = None
    questions = None
    entrance_extra_data = None

    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.prefetch_related('booklet', 'booklet__entrance',
                                                                        'booklet__entrance__organization',
                                                                        'booklet__entrance__entrance_type',
                                                                        'booklet__entrance__entrance_set',
                                                                        'lesson').get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        # booklet_detail record exist --> fetch questions
        questions = booklet_detail.questions.all().order_by('question_number')

        try:
            entrance_extra_data = json.loads(booklet_detail.booklet.entrance.extra_data, encoding="utf-8")
        except:
            pass

        if request.method == "GET":
            form = EntranceQuestionEditForm(ebd_id=booklet_detail.id)
            form2 = EntranceQuestionEditByFileForm()
        elif request.method == "POST":
            form = EntranceQuestionEditForm(ebd_id=booklet_detail.id, data=request.POST)

            if form.is_valid():
                # get question record
                question_no = form.cleaned_data['question_number']
                answer_key = form.cleaned_data['answer_key']

                try:
                    question = EntranceQuestion.objects.get(question_number=question_no, booklet_detail=booklet_detail)

                    old_answer = question.answer_key
                    new_answer = int(answer_key)

                    question.answer_key = answer_key
                    question.save()

                    # generate log
                    elt = EntranceLogType.objects.get(title="change_question_answer")

                    log = {"qid": question.id, "qno": question_no, "old": old_answer, "new": new_answer}
                    json_log = json.dumps(log)

                    log_rec = EntranceLog(log_type=elt, data=json_log, entrance=booklet_detail.booklet.entrance)
                    log_rec.save()
                    # end generate log

                    return redirect('admin.de_entrance.questions.list', pk=booklet_detail.id)
                except IntegrityError:
                    has_form_message = True
                    form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, booklet_detail=booklet_detail, questions=questions,
             has_error=has_error, error_no=error_no, form=form, form2=form2, has_form_message=has_form_message,
             form_message=form_message, edata=entrance_extra_data, minnersel=inner_menu_selected,
             menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_questions_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_file_change(request, pk):
    has_error = False
    booklet_detail = None
    questions = None

    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.prefetch_related('booklet', 'booklet__entrance',
                                                                        'booklet__entrance__organization',
                                                                        'booklet__entrance__entrance_type',
                                                                        'booklet__entrance__entrance_set',
                                                                        'lesson').get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == "POST":
            form = EntranceQuestionEditByFileForm(request.POST or None, request.FILES)

            if form.is_valid():
                # get question record

                file = request.FILES['file']

                for line in file.readlines():
                    split_array = line.split(',')
                    question_no = int(split_array[0].strip())
                    answer_key = int(split_array[1].strip())

                    try:
                        question = EntranceQuestion.objects.get(question_number=question_no,
                                                                booklet_detail=booklet_detail)

                        old_answer = question.answer_key
                        new_answer = int(answer_key)

                        question.answer_key = answer_key
                        question.save()

                        # generate log
                        elt = EntranceLogType.objects.get(title="change_question_answer")

                        log = {"qid": question.id, "qno": question_no, "old": old_answer, "new": new_answer}
                        json_log = json.dumps(log)

                        log_rec = EntranceLog(log_type=elt, data=json_log, entrance=booklet_detail.booklet.entrance)
                        log_rec.save()
                        # end generate log

                    except IntegrityError:
                        pass

    return redirect('admin.de_entrance.questions.list', pk=booklet_detail.id)


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_generate_all(request, pk):
    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.get(pk=pk)

        # booklet_detail record exist
        for i in xrange(booklet_detail.q_from, booklet_detail.q_to + 1):
            question = EntranceQuestion(question_number=i, answer_key=1, booklet_detail=booklet_detail)
            question.save()

        return redirect('admin.de_entrance.questions.list', pk=booklet_detail.id)

    except:
        return redirect('admin.de_entrance')


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_picture_list(request, pk):
    # pk = EntranceBookletDetail__id
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1

    booklet_detail = None
    questions = None
    entrance_extra_data = None

    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.prefetch_related('booklet', 'booklet__entrance',
                                                                        'booklet__entrance__organization',
                                                                        'booklet__entrance__entrance_type',
                                                                        'booklet__entrance__entrance_set',
                                                                        'lesson').get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        questions = booklet_detail.questions.all().prefetch_related('qs_images').order_by('question_number')

        try:
            entrance_extra_data = json.loads(booklet_detail.booklet.entrance.extra_data, encoding="utf-8")
        except:
            pass

        if request.method == "GET":
            form = EntranceQuestionPictureAddForm(ebd_id=booklet_detail.id)
        elif request.method == "POST":
            form = EntranceQuestionPictureAddForm(ebd_id=booklet_detail.id, data=request.POST, files=request.FILES)

            if form.is_valid():

                question_no = form.cleaned_data['question'].id
                try:
                    # question_record = EntranceQuestion.objects.get(question_number=question_no, booklet_detail=booklet_detail)
                    # question record exist --> generate Question Image record
                    image_record = form.save(commit=False)
                    # image_record.question = question_record
                    image_record.save()

                    # generate log
                    elt = EntranceLogType.objects.get(title="new_question_image")

                    log = {"qid": image_record.question.id,
                           "qno": image_record.question.question_number,
                           "img_order": image_record.order,
                           "img_url": image_record.image.url,
                           "img_key": image_record.unique_key.get_hex()}
                    json_log = json.dumps(log)

                    log_rec = EntranceLog(log_type=elt, data=json_log, entrance=booklet_detail.booklet.entrance)
                    log_rec.save()
                    # end generate log

                    return redirect('admin.de_entrance.pquestions.list', pk=booklet_detail.id)

                except IntegrityError, exc:
                    has_form_message = True
                    form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, booklet_detail=booklet_detail, questions=questions,
             has_error=has_error, error_no=error_no, form=form,
             has_form_message=has_form_message, form_message=form_message, edata=entrance_extra_data,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_pquestions_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_picture_ajax(request, pk):
    form = None
    has_error = False
    booklet_detail = None

    result = {}

    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.prefetch_related('booklet', 'booklet__entrance',
                                                                        'booklet__entrance__organization',
                                                                        'booklet__entrance__entrance_type',
                                                                        'booklet__entrance__entrance_set',
                                                                        'lesson').get(pk=pk)
    except:
        has_error = True
        error_no = 1
        result = {"status": "Error"}

    if not has_error:
        request.POST["question"] = (436, 1)
        request.POST["order"] = 1

        image = request.FILES.get('image', None)

        if image is not None:
            names = image.name.split('.')[0].split('-')

            try:
                # get question record
                question = EntranceQuestion.objects.get(booklet_detail=booklet_detail, question_number=int(names[0]))

                form = EntranceQuestionPictureAddForm2(data=request.POST, files=request.FILES)
                if form.is_valid():

                    try:
                        # question record exist --> generate Question Image record
                        image_record = form.save(commit=False)
                        order = int(names[1]) if len(names) > 1 else 1
                        image_record.order = order
                        image_record.question = question
                        image_record.save()

                        # generate log
                        elt = EntranceLogType.objects.get(title="new_question_image")

                        log = {"qid": image_record.question.id,
                               "qno": image_record.question.question_number,
                               "img_order": image_record.order,
                               "img_url": image_record.image.url,
                               "img_key": image_record.unique_key.get_hex()}
                        json_log = json.dumps(log)

                        log_rec = EntranceLog(log_type=elt, data=json_log, entrance=booklet_detail.booklet.entrance)
                        log_rec.save()
                        # end generate log

                        delete_link = reverse('admin.de_entrance.pquestions.del', kwargs={'pk': image_record.id})
                        log["delete_link"] = delete_link

                        result = {"status": "OK", "data": log}

                    except IntegrityError, exc:
                        result = {"status": "Error", "error_type": "DUPLICATE"}
                        pass

                else:
                    result = {"status": "Error", "error_type": "INVALID"}
            except Exception, exc:
                print exc
                result = {"status": "Error", "error_type": "INVALID"}
        else:
            result = {"status": "Error", "error_type": "INVALID"}

    print result
    return JsonResponse(result)


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_picture_del(request, pk):
    ebd_id = -1
    try:
        img_record = EntranceQuestionImages.objects.get(pk=pk)
        ebd_id = img_record.question.booklet_detail.id
        entrance = img_record.question.booklet_detail.booklet.entrance
        img_record.delete()

        # generate log
        elt = EntranceLogType.objects.get(title="del_question_image")

        log = {"qid": img_record.question.id,
               "qno": img_record.question.question_number,
               "img_order": img_record.order,
               "img_key": img_record.unique_key.get_hex()}
        json_log = json.dumps(log)

        log_rec = EntranceLog(log_type=elt, data=json_log, entrance=entrance)
        log_rec.save()
        # end generate log
    except:
        pass

    if ebd_id > 0:
        return redirect('admin.de_entrance.pquestions.list', pk=ebd_id)

    return redirect('admin.de_entrance')


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_change_is_editing(request, pk, state):
    try:
        entrance_record = Entrance.objects.get(pk=pk)

        if state == "start":
            entrance_record.is_editing = True
            entrance_record.save()
        elif state == "done":
            entrance_record.is_editing = False
            entrance_record.save()
    except:
        pass

    return redirect("admin.de_entrance.booklets", pk=pk)


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_extra_data_add(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1
    entrance_record = None

    # Get entrance record
    try:
        entrance_record = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                            'entrance_set__group').get(pk=pk)

    except Exception, exc:
        print exc
        has_error = True
        error_no = 1

    if not has_error:
        if request.method == "GET":
            form = EntranceExtraDataAddForm()
        elif request.method == "POST":
            form = EntranceExtraDataAddForm(request.POST or None)

            if form.is_valid():
                data_key = form.cleaned_data['data_key']
                data_value = form.cleaned_data['data_value']

                try:
                    extra_data = json.loads(entrance_record.extra_data, encoding="utf-8")
                except ValueError:
                    # some error on parsing json data
                    extra_data = {}

                extra_data[data_key] = data_value
                result = json.dumps(extra_data)

                entrance_record.extra_data = result

                try:
                    entrance_record.save()

                    # generate log
                    elt = EntranceLogType.objects.get(title="create_extra_data")
                    log = {}
                    json_log = json.dumps(log)

                    log_rec = EntranceLog(log_type=elt, data=json_log, entrance=entrance_record)
                    log_rec.save()

                    return redirect("admin.de_entrance.booklets", pk=entrance_record.id)
                except:
                    has_form_message = True
                    form_message = 2

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrance=entrance_record, has_error=has_error,
             error_no=error_no,
             form=form, has_form_message=has_form_message, form_message=form_message,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_extradata_add.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_extra_data_clear(request, pk):
    # Get entrance record
    try:
        entrance_record = Entrance.objects.get(pk=pk)
        entrance_record.extra_data = ""
        entrance_record.save()

        # generate log
        elt = EntranceLogType.objects.get(title="clear_extra_data")
        log = {}
        json_log = json.dumps(log)

        log_rec = EntranceLog(log_type=elt, data=json_log, entrance=entrance_record)
        log_rec.save()

    except:
        pass

    return redirect("admin.de_entrance.booklets", pk=pk)


@login_required
@group_permission_required('main.de_entrance_publish', raise_exception=True)
def create_package(request, pk):
    # Get Entrance record
    try:
        entrance_record = Entrance.objects.prefetch_related("organization",
                                                            "entrance_type",
                                                            "entrance_set",
                                                            "entrance_set__group"
                                                            ).get(pk=pk)

        package_type_create_record = EntrancePackageType.objects.get(title="CREATE")
        package_type_update_record = EntrancePackageType.objects.get(title="UPDATE")

        if entrance_record.published:
            # entrance published before
            extra_data_changed_flag = False

            published_package_record = EntrancePackage.objects.get(entrance=entrance_record,
                                                                   package_type=package_type_create_record)

            if published_package_record:

                # get json data from it
                print published_package_record.content
                data = json.loads(published_package_record.content)
                minified_data = json.loads(published_package_record.minified)

                data_init = data["init"]

                cachalot.api.invalidate(EntranceLog)
                # load data changes from log table
                logs = EntranceLog.objects.filter(entrance=entrance_record) \
                    .filter(log_time__gt=published_package_record.create_time) \
                    .prefetch_related('log_type')

                if logs:
                    # logs exists -> so create change attribute

                    image_deleted_list = []
                    image_added_list = []  # to create new package for it
                    has_package_file = False

                    for log in logs:
                        log_data = json.loads(log.data)

                        if log.log_type.title == "change_question_answer":
                            # find data in log record
                            for booklet_index in xrange(len(data_init['entrance.booklets'])):
                                lessons = data_init['entrance.booklets'][booklet_index]['lessons']
                                for lesson_index in xrange(len(lessons)):
                                    questions = data_init['entrance.booklets'][booklet_index]['lessons'][lesson_index][
                                        "questions"]
                                    for q_index in xrange(len(questions)):
                                        if int(questions[q_index]['number']) == int(log_data['qno']):
                                            data["init"]['entrance.booklets'][booklet_index]['lessons'][lesson_index][
                                                "questions"][q_index]['answer_key'] = log_data['new']
                                            break

                        elif log.log_type.title == "del_question_image":
                            # add it to change.images deleted list
                            image_deleted_list.append(log_data['img_key'])

                            # find data in log record
                            for booklet in data_init['entrance.booklets']:
                                for lesson in booklet['lessons']:
                                    for q in lesson['questions']:
                                        if q['number'] == log_data['qno']:
                                            for img in q['images']:
                                                if img['order'] == log_data['img_order']:
                                                    del img
                                                    break

                        elif log.log_type.title == "new_question_image":

                            # add it to list
                            image_added_list.append(log_data["img_url"])

                            # find data in log record
                            for booklet in data_init['entrance.booklets']:
                                for lesson in booklet['lessons']:
                                    for q in lesson['questions']:
                                        if q['number'] == log_data['qno']:
                                            for img in q['images']:
                                                if img['order'] == log_data['img_order']:
                                                    img["unique_key"] = log_data["img_key"]
                                                    break

                                            q["images"].append({
                                                "order": log_data["img_order"],
                                                "unique_key": log_data["img_key"]
                                            })
                                            break

                        elif log.log_type.title == "create_extra_data" or log.log_type.title == "clear_extra_data":
                            extra_data_changed_flag = True
                            if entrance_record.extra_data != "":
                                data_init["extra_data"] = json.loads(entrance_record.extra_data)
                                minified_data["init"]["extra_data"] = json.loads(entrance_record.extra_data)
                            else:
                                data_init["extra_data"] = ""
                                minified_data["init"]["extra_data"] = ""

                    now = datetime.now(tz=pytz.utc)
                    new_uuid = uuid.uuid4()

                    data_init['last_update'] = str(now)
                    data["last_update"] = str(now)

                    minified_data["init"]['last_update'] = str(now)
                    minified_data["last_update"] = str(now)

                    # first save initial record
                    published_package_record.content = json.dumps(data)
                    published_package_record.minified = json.dumps(minified_data)
                    published_package_record.update_time = now
                    published_package_record.save()

                    if len(image_added_list) > 0:
                        # image added to file
                        create_package_file(new_uuid, image_added_list)
                        create_package_file2(new_uuid, image_added_list)
                        has_package_file = True

                    data['change-{}'.format(new_uuid.get_hex())] = {
                        "package.unique_key": new_uuid.get_hex(),
                        "create_time": str(now),
                        "images.deleted": image_deleted_list,
                        "has_package_file": has_package_file,
                        "has_extra_data": extra_data_changed_flag
                    }
                    minified_data['change-{}'.format(new_uuid.get_hex())] = {
                        "package.unique_key": new_uuid.get_hex(),
                        "create_time": str(now),
                        "images.deleted": [],
                        "has_package_file": has_package_file,
                        "has_extra_data": extra_data_changed_flag
                    }

                    # create package record
                    json_data = json.dumps(data)
                    minified_json_data = json.dumps(minified_data)

                    # creating record
                    package_record = EntrancePackage(entrance=entrance_record,
                                                     package_type=package_type_update_record,
                                                     create_time=now,
                                                     update_time=now,
                                                     unique_key=new_uuid,
                                                     content=json_data,
                                                     minified=minified_json_data)
                    package_record.save()

                    # recreate INITIAL record
                    images = EntranceQuestionImages.objects.filter(
                        question__booklet_detail__booklet__entrance=entrance_record)
                    initial_images_list = [rec.image.url for rec in images]
                    # create_package_file(published_package_record.unique_key, initial_images_list)
                    # create_package_file2(published_package_record.unique_key, initial_images_list)

                    # update entrance_record publish status
                    entrance_record.published = True
                    entrance_record.last_published = datetime.now()
                    entrance_record.save()

                    # Create activity log
                    create_concough_activity(CONCOUGH_LOG_TYPES[1], entrance_record)

        else:
            # first entrance package publish
            # first create starter dictionary

            # Get Package Type of "CREATE"

            (data, minified_data, imageFilesList) = create_package_record(entrance_record)

            # create directory in tmp device --> first remove existing
            package_unique_key = uuid.uuid4()
            data["init"]["package.unique_key"] = package_unique_key.get_hex()
            minified_data["init"]["package.unique_key"] = package_unique_key.get_hex()

            # create_package_file(package_unique_key, imageFilesList)
            # create_package_file2(package_unique_key, imageFilesList)

            # now time in utc
            now = datetime.now(tz=pytz.utc)
            data["last_update"] = str(now)
            data["init"]["create_time"] = str(now)
            minified_data["last_update"] = str(now)
            minified_data["init"]["create_time"] = str(now)

            json_data = json.dumps(data)
            minified_json_data = json.dumps(minified_data)

            # creating record
            package_record = EntrancePackage(entrance=entrance_record,
                                             package_type=package_type_create_record,
                                             create_time=now,
                                             update_time=now,
                                             unique_key=package_unique_key,
                                             content=json_data,
                                             minified=minified_json_data)
            package_record.save()

            # update entrance_record publish status
            entrance_record.published = True
            entrance_record.last_published = datetime.now()
            entrance_record.save()

            # Create activity log
            create_concough_activity(CONCOUGH_LOG_TYPES[0], entrance_record)
            create_product_statistic(entrance_record)

    except Exception, exc:
        print exc
        # Entrance record does not exist
        pass

    return redirect("admin.de_entrance.booklets", pk=pk)


def create_package_file(package_unique_key, imageFilesList):
    temp_dir_path = "/tmp/{}".format(package_unique_key.get_hex())

    if os.path.exists(temp_dir_path):
        os.rmdir(temp_dir_path)

    os.mkdir(temp_dir_path)
    if os.path.exists(temp_dir_path):
        for image_file in imageFilesList:
            real_path = os.path.realpath(image_file[1:])
            file_name = os.path.basename(real_path)
            shutil.copy2(real_path, "{}/{}".format(temp_dir_path, file_name))

    # create compress file
    lz4tools.compressTarDefault(temp_dir_path, True, "{}.lz4".format(temp_dir_path))

    # copy file to media folder
    new_package_file_path = os.path.join(settings.MEDIA_ROOT, "packages", "{}.lz4".format(package_unique_key.get_hex()))
    shutil.move("{}.lz4".format(temp_dir_path), new_package_file_path)

    # os.rmdir(temp_dir_path)
    shutil.rmtree(temp_dir_path, True)


def create_package_file2(package_unique_key, imageFilesList):
    result = {}
    for image_file in imageFilesList:
        # real_path = os.path.join(settings.MEDIA_ROOT, image_file)
        real_path = os.path.realpath(image_file[1:])
        file_name = os.path.basename(real_path)

        file = open(real_path, 'r+b')
        file_content = file.read()

        base64_content = file_content.encode("base64")
        file.close()

        unique_key = str(file_name).split('.')

        result[unique_key[0]] = base64_content

    # copy file to media folder
    new_package_file_path = os.path.join(settings.MEDIA_ROOT, "packages", "{}.pkg".format(package_unique_key.get_hex()))
    if os.path.exists(os.path.realpath(new_package_file_path)):
        os.remove(os.path.realpath(new_package_file_path))
    new_file = open(new_package_file_path, 'w')
    new_file.write(json.dumps(result))
    new_file.close()


def create_package_record(entrance_record):
    imageFilesList = []
    minified_data = {}

    data = {"entrance.unique_key": entrance_record.unique_key.get_hex(),
            "last_update": None,
            "entrance.organization.name": entrance_record.organization.title,
            "entrance.set.name": entrance_record.entrance_set.title,
            "entrance.type.name": entrance_record.entrance_type.title,
            "entrance.group.name": entrance_record.entrance_set.group.title,
            "entrance.year": entrance_record.year,
            "entrance.month": entrance_record.month,
            "entrance.set.image": None,
            "init": {},
            }

    if entrance_record.entrance_set.image:
        data["entrance.set.id"] = entrance_record.entrance_set.id

    data["init"] = {"package.unique_key": "",
                    "create_time": None,
                    "entrance.booklets.count": 0,
                    "entrance.booklets": [],
                    "extra_data": "",
                    }

    # fill extra data from entrance
    if entrance_record.extra_data != "":
        extra_data = json.loads(entrance_record.extra_data)
        data["init"]["extra_data"] = extra_data

    # get pooklets from db
    entrance_booklets = EntranceBooklet.objects.filter(entrance=entrance_record).order_by('order')
    eb_count = entrance_booklets.count()
    if eb_count > 0:
        data["init"]["entrance.booklets.count"] = eb_count
        minified_data = copy.deepcopy(data)

        booklets_ref = data["init"]["entrance.booklets"]
        for booklet in entrance_booklets:
            booklet_ref = {
                "title": booklet.title,
                "is_optional": booklet.optional,
                "duration": booklet.duration,
                "order": booklet.order,
                "lessons.count": 0,
                "lessons": []
            }
            booklets_ref.append(booklet_ref)

            # get lessons from booklet details
            entrane_booklet_detail = EntranceBookletDetail.objects.filter(booklet=booklet) \
                .prefetch_related("lesson").order_by('order')

            ebd = entrane_booklet_detail.count()
            if ebd > 0:
                booklet_ref["lessons.count"] = ebd

                lessons_ref = booklet_ref["lessons"]
                for entrance_bd in entrane_booklet_detail:
                    lesson_ref = {
                        "title": entrance_bd.lesson.title,
                        "full_title": entrance_bd.lesson.full_title,
                        "q_start": entrance_bd.q_from,
                        "q_end": entrance_bd.q_to,
                        "q_count": entrance_bd.q_count,
                        "order": entrance_bd.order,
                        "duration": entrance_bd.duration,
                        "questions": []
                    }
                    lessons_ref.append(lesson_ref)

                    # get questions from entrance questions
                    entrance_questions = EntranceQuestion.objects.filter(booklet_detail=entrance_bd).prefetch_related(
                        'qs_images') \
                        .order_by('question_number')

                    if entrance_questions:
                        questions_ref = lesson_ref['questions']
                        for q in entrance_questions:
                            question_ref = {
                                "number": q.question_number,
                                "answer_key": q.answer_key,
                                "images": []
                            }
                            questions_ref.append(question_ref)

                            # get question pictures
                            entrance_question_images = q.qs_images.all()

                            if entrance_question_images:
                                eq_images_ref = question_ref["images"]
                                for img in entrance_question_images:
                                    eq_images_ref.append({
                                        "order": img.order,
                                        "unique_key": img.unique_key.get_hex()
                                    })
                                    imageFilesList.append(img.image.url)
                            else:
                                # No Images for question
                                # raise Exception("No Images for question")
                                pass

                    else:
                        # No Questions
                        raise Exception("No Questions")
                        pass

            else:
                # No booklet details
                raise Exception("No Booklet Details")
                pass

    else:
        # No Booklets
        raise Exception("No Booklets")
        pass

    return data, minified_data, imageFilesList


@login_required
@group_permission_required('main.de_entrance_publish', raise_exception=True)
def list_package(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    entrance_record = None
    packages = []
    has_error = False
    error_no = -1

    # Get entrance record
    try:
        entrance_record = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                            'entrance_set__group').get(pk=pk)

        packages = EntrancePackage.objects.values('id', 'package_type__title', 'create_time', 'unique_key') \
            .filter(entrance=entrance_record).prefetch_related('package_type').order_by("package_type", "create_time")
    except Exception, exc:
        has_error = True
        error_no = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrance=entrance_record,
             has_error=has_error, error_no=error_no, packages=packages,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    return render_to_response("admin/de_entrance/packages_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_publish', raise_exception=True)
def reset_package(request, pk):
    try:
        entrance = Entrance.objects.get(pk=pk)

        packages = EntrancePackage.objects.filter(entrance=entrance)
        if len(packages) <= 0:
            entrance.published = False
            entrance.last_published = None
            entrance.save()

    except Exception, exc:
        pass

    return redirect("admin.de_entrance.booklets", pk=pk)


@login_required
@group_permission_required('main.de_entrance_publish', raise_exception=True)
def delete_package(request, pk):
    entrance_id = -1

    try:
        package = EntrancePackage.objects.prefetch_related('package_type', 'entrance').get(pk=pk)
        entrance_id = package.entrance.id
        package_type_title = package.package_type.title

        new_package_file_path = os.path.join(settings.MEDIA_ROOT,
                                             "packages",
                                             "{}.lz4".format(package.unique_key.get_hex()))
        new_package_file_path2 = os.path.join(settings.MEDIA_ROOT,
                                              "packages",
                                              "{}.pkg".format(package.unique_key.get_hex()))

        if os.path.exists(new_package_file_path):
            os.remove(new_package_file_path)
        if os.path.exists(new_package_file_path2):
            os.remove(new_package_file_path2)

        # delete ConcoughActivity record
        entrance = package.entrance
        activity = ConcoughActivity.objects.filter(entrance=entrance, activity_type="ENTRANCE_%s" % package_type_title)
        activity.delete()

        # delete package from media
        package.delete()

    except Exception, exc:
        print exc
        pass

    if entrance_id > 0:
        return redirect("admin.de_entrance.publish.list", pk=entrance_id)

    return redirect("admin.de_entrance")


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_create_job(request):
    try:
        db = connectToMongo()

        if request.method == "POST":
            form = EntranceJobAssignForm(request.POST or None, files=request.FILES)

            if form.is_valid():
                selected_user = form.cleaned_data["job_supervisor"]
                orig_file = form.cleaned_data["orig_file"]
                pk = form.cleaned_data["entrance_id"]
                owner_user = User.objects.get(pk=selected_user.id)

                entrance = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                             'entrance_set__group').get(pk=pk)

                job = db.job.find_one({"job_relate_uniqueid": entrance.unique_key})

                owner_obj = {
                    "user_id": owner_user.id,
                    "username": owner_user.username,
                    "fullname": owner_user.get_full_name(),
                    "joined": owner_user.date_joined
                }

                fs = GridFS(db)
                fs_obj = fs.put(orig_file,
                                content_type='application/x-rar-compressed, application/octet-stream, application/zip')

                if job is None:
                    booklets = EntranceBooklet.objects.filter(entrance=entrance).prefetch_related('bookletdetails',
                                                                                                  'bookletdetails__lesson').order_by(
                        'order')

                    job = {
                        "job_owner": owner_obj,
                        "job_owner_id": owner_user.id,
                        "job_type": "ENTRANCE",
                        "job_main_file": fs_obj,
                        "created": datetime.now(tz=pytz.UTC),
                        "updated": datetime.now(tz=pytz.UTC),
                        "status": "CREATED",
                        "job_relate_uniqueid": entrance.unique_key,
                        "data": {
                            "organization": unicode(entrance.organization.title),
                            "type": unicode(entrance.entrance_type.title),
                            "group": unicode(entrance.entrance_set.group.title),
                            "set": unicode(entrance.entrance_set.title),
                            "year": unicode(entrance.year),
                            "month": unicode(entrance.month),
                            "tasks": []
                        }
                    }

                    lessons = []
                    for b in booklets:
                        booklet_details = b.bookletdetails.all()

                        for detail in booklet_details:
                            lessons.append({
                                "state": "CREATED",
                                "task_unique_id": uuid.uuid4(),
                                "main_editor": None,
                                "holding_editor": None,
                                "checkers": [],
                                "created": datetime.now(tz=pytz.UTC),
                                "updated": datetime.now(tz=pytz.UTC),
                                "lesson_title": detail.lesson.full_title,
                                "q_count": detail.q_count,
                                "price_per_q": 0,
                                "orig_file": None,
                                "term_file": None,
                                "main_term_file": None,
                                "log": []
                            })

                    job["data"]["tasks"] = lessons

                    db.job.insert(job)

                    entrance.assigned_to_task = True
                    entrance.save()
                else:
                    db.job.update_one({"job_relate_uniqueid": entrance.unique_key}, {
                        '$set': {
                            'job_owner': owner_obj,
                            "job_main_file": fs_obj
                        }
                    })

                return redirect('admin.de_jobs.entrance.list')

    except Exception, exc:
        print exc

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_multi_list(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_multi_list"

    page = request.GET.get('page', 1)
    entrance_list = EntranceMulti.objects.all() \
        .prefetch_related('entrances') \
        .order_by('published', '-updated', '-created')

    paginator = Paginator(entrance_list, 20)
    try:
        entrances = paginator.page(page)
    except PageNotAnInteger:
        entrances = paginator.page(1)
    except EmptyPage:
        entrances = paginator.page(paginator.num_pages)

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrances=entrances, minnersel=inner_menu_selected,
             menuinner=entrance_menus)
    return render_to_response("admin/de_entrance/entrance_multi_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_multi_add(request):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_multi_list"

    has_form_message = False
    form_message = -1

    _type = request.GET.get('type', -1)
    type_list = EntranceType.objects.all()

    group = request.GET.get('group', -1)
    group_list = None
    if _type > 0:
        group_list = ExaminationGroup.objects.filter(etype__id=_type)

    _set = request.GET.get('set', -1)
    set_list = None
    if group > 0:
        set_list = EntranceSet.objects.filter(group__id=group)

    form = None
    if _set > 0:
        if request.method == "GET":
            form = EntranceMultiAddForm(set_id=_set)
        elif request.method == "POST":
            form = EntranceMultiAddForm(set_id=_set, data=request.POST or None)

            print form.errors
            if form.is_valid():

                entrance_multi = form.save()
                return redirect("admin.de_entrance_multi")
            else:
                has_form_message = True
                form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected,
             menuinner=entrance_menus, type=int(_type), type_list=type_list, group_list=group_list, group=int(group),
             set_list=set_list, set=int(_set), form=form, has_form_message=has_form_message, form_message=form_message)
    return render_to_response("admin/de_entrance/entrance_multi_add.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_multi_publish(request, pk):
    try:
        emulti = EntranceMulti.objects.get(pk=pk)

        activity = ConcoughActivity.objects.filter(entrancemulti=emulti, activity_type=CONCOUGH_LOG_TYPES_2[2])
        if len(activity) == 0:
            create_concough_activity(CONCOUGH_LOG_TYPES_2[2], emulti)

            emulti.published = True
            emulti.save()
    except:
        pass

    return redirect("admin.de_entrance_multi")


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_multi_unpublish(request, pk):
    try:
        emulti = EntranceMulti.objects.get(pk=pk)

        activity = ConcoughActivity.objects.filter(entrancemulti=emulti, activity_type=CONCOUGH_LOG_TYPES_2[2])
        activity.delete()

        emulti.published = False
        emulti.save()
    except:
        pass

    return redirect("admin.de_entrance_multi")


@login_required
@group_permission_required('main.de_entrance_detail', raise_exception=True)
def entrance_multi_del(request, pk):
    try:
        emulti = EntranceMulti.objects.get(pk=pk)

        if emulti.published == False:
            emulti.delete()
    except:
        pass

    return redirect("admin.de_entrance_multi")


# 2019-04-23
@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_tags_list(request, pk):
    # pk = EntranceBookletDetail__id
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    form = None
    form2 = None
    has_error = False
    error_no = -1
    has_form_message = False
    form_message = -1

    booklet_detail = None
    questions = None
    entrance_extra_data = None

    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.prefetch_related('booklet', 'booklet__entrance',
                                                                        'booklet__entrance__organization',
                                                                        'booklet__entrance__entrance_type',
                                                                        'booklet__entrance__entrance_set',
                                                                        'lesson').get(pk=pk)
    except:
        has_error = True
        error_no = 1

    if not has_error:
        form = EntranceQuestionTagAddForm(ebd_id=booklet_detail.id)
        form2 = EntranceQuestionTagFileForm()

        questions = booklet_detail.questions.all().prefetch_related('tags').order_by('question_number')

        try:
            entrance_extra_data = json.loads(booklet_detail.booklet.entrance.extra_data, encoding="utf-8")
        except:
            pass

        # if request.method == "GET":
        #     form = EntranceQuestionPictureAddForm(ebd_id=booklet_detail.id)
        # elif request.method == "POST":
        #     form = EntranceQuestionPictureAddForm(ebd_id=booklet_detail.id, data=request.POST, files=request.FILES)
        #
        #     if form.is_valid():
        #
        #         question_no = form.cleaned_data['question'].id
        #         try:
        #             # question_record = EntranceQuestion.objects.get(question_number=question_no, booklet_detail=booklet_detail)
        #             # question record exist --> generate Question Image record
        #             image_record = form.save(commit=False)
        #             # image_record.question = question_record
        #             image_record.save()
        #
        #             # generate log
        #             elt = EntranceLogType.objects.get(title="new_question_image")
        #
        #             log = {"qid": image_record.question.id,
        #                    "qno": image_record.question.question_number,
        #                    "img_order": image_record.order,
        #                    "img_url": image_record.image.url,
        #                    "img_key": image_record.unique_key.get_hex()}
        #             json_log = json.dumps(log)
        #
        #             log_rec = EntranceLog(log_type=elt, data=json_log, entrance=booklet_detail.booklet.entrance)
        #             log_rec.save()
        #             # end generate log
        #
        #             return redirect('admin.de_entrance.pquestions.list', pk=booklet_detail.id)
        #
        #         except IntegrityError, exc:
        #             has_form_message = True
        #             form_message = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, booklet_detail=booklet_detail, questions=questions,
             has_error=has_error, error_no=error_no, form=form, form2=form2,
             has_form_message=has_form_message, form_message=form_message, edata=entrance_extra_data,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    d.update(csrf(request))
    return render_to_response("admin/de_entrance/entrance_tags_list.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_tags_add(request, pk):
    if request.method == "POST":
        form = EntranceQuestionTagAddForm(ebd_id=pk, data=request.POST)

        if form.is_valid():
            if "options" in form.data:
                question_id = form.cleaned_data["question"].id
                options = form.data["options"]

                try:
                    question = EntranceQuestion.objects.get(id=question_id, booklet_detail__id=pk)
                    tag = Tags.objects.get(pk=options)

                    question.tags.add(tag)

                    package = EntranceLessonTagPackage.objects.filter(booklet_detail__id=pk).first()
                    if package is not None:
                        package.is_changed = True
                        package.save()

                    # generate log
                    elt = EntranceLogType.objects.get(title="tag_add")

                    log = {"qid": question.id, "qno": question.question_number, "tid": tag.id}
                    json_log = json.dumps(log)

                    log_rec = EntranceLog(log_type=elt, data=json_log, entrance=question.booklet_detail.booklet.entrance)
                    log_rec.save()
                    # end generate log

                except Exception:
                    pass

            else:
                question_id = form.cleaned_data["question"].id
                title = form.cleaned_data["title"]

                try:
                    question = EntranceQuestion.objects.get(id=question_id, booklet_detail__id=pk)
                    t = question.tags.create(title=title)

                    package = EntranceLessonTagPackage.objects.filter(booklet_detail__id=pk).first()
                    if package is not None:
                        package.is_changed = True
                        package.save()

                    # generate log
                    elt = EntranceLogType.objects.get(title="tag_add")

                    log = {"qid": question.id, "qno": question.question_number, "tid": t.id}
                    json_log = json.dumps(log)

                    log_rec = EntranceLog(log_type=elt, data=json_log, entrance=question.booklet_detail.booklet.entrance)
                    log_rec.save()
                    # end generate log

                except Exception, exc:
                    pass

    return redirect('admin.de_entrance.tags.list', pk=pk)


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_tags_del(request, pk, qid, tid):
    try:
        question = EntranceQuestion.objects.get(id=qid, booklet_detail__id=pk)
        tag = Tags.objects.get(pk=tid)

        question.tags.remove(tag)

        package = EntranceLessonTagPackage.objects.filter(booklet_detail__id=pk).first()
        if package is not None:
            package.is_changed = True
            package.save()

        # generate log
        elt = EntranceLogType.objects.get(title="tag_remove")

        log = {"qid": question.id, "qno": question.question_number, "tid": tag.id}
        json_log = json.dumps(log)

        log_rec = EntranceLog(log_type=elt, data=json_log, entrance=question.booklet_detail.booklet.entrance)
        log_rec.save()
        # end generate log

    except:
        pass

    return redirect('admin.de_entrance.tags.list', pk=pk)


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_question_tags_file(request, pk):
    has_error = False
    booklet_detail = None

    try:
        # get booklet_detail_record
        booklet_detail = EntranceBookletDetail.objects.get(pk=pk)
    except:
        has_error = True

    if not has_error:
        if request.method == "POST":
            form = EntranceQuestionTagFileForm(request.POST or None, request.FILES)

            if form.is_valid():
                # get question record
                file = request.FILES['file']

                for line in file.readlines():
                    split_array = line.split(',')
                    print split_array

                    question_no = int(split_array[0].strip())

                    try:
                        question = EntranceQuestion.objects.get(question_number=question_no,
                                                                booklet_detail=booklet_detail)

                        for tag in question.tags.all():
                            # generate log
                            elt = EntranceLogType.objects.get(title="tag_remove")

                            log = {"qid": question.id, "qno": question.question_number, "tid": tag.id}
                            json_log = json.dumps(log)

                            log_rec = EntranceLog(log_type=elt, data=json_log,
                                                  entrance=question.booklet_detail.booklet.entrance)
                            log_rec.save()
                            # end generate log

                        # clear tags from question
                        question.tags.clear()

                        for tag in split_array[1:]:
                            title = tag.strip().replace('\r', '').replace('\n', '')
                            if title != "":

                                tags = Tags.objects.filter(title__exact=title)
                                t = None
                                if len(tags) > 0:
                                    t = tags[0]

                                if t is not None:
                                    question.tags.add(t)
                                else:
                                    t = question.tags.create(title=tag.strip())

                                # generate log
                                elt = EntranceLogType.objects.get(title="tag_add")

                                log = {"qid": question.id, "qno": question.question_number, "tid": t.id}
                                json_log = json.dumps(log)

                                log_rec = EntranceLog(log_type=elt, data=json_log,
                                                      entrance=question.booklet_detail.booklet.entrance)
                                log_rec.save()
                                # end generate log

                        package = EntranceLessonTagPackage.objects.filter(booklet_detail=booklet_detail).first()
                        if package is not None:
                            package.is_changed = True
                            package.save()

                    except IntegrityError:
                        pass

    return redirect('admin.de_entrance.tags.list', pk=pk)


@login_required
@group_permission_required('main.de_questions', raise_exception=True)
def entrance_tags_package_list(request, pk):
    menu_selected = "entrances"
    inner_menu_selected = "entrance_list"

    entrance_record = None
    packages = []
    booklet_details = []
    has_error = False
    error_no = -1

    # Get entrance record
    try:
        entrance_record = Entrance.objects.prefetch_related('organization', 'entrance_type', 'entrance_set',
                                                            'entrance_set__group').get(pk=pk)

        packages = EntranceLessonTagPackage.objects\
            .prefetch_related('booklet_detail', 'booklet_detail__lesson').filter(booklet_detail__booklet__entrance=entrance_record)


        ids = []
        for p in packages:
            ids.append(p.booklet_detail.id)

        print ids
        booklet_details = EntranceBookletDetail.objects.filter(booklet__entrance=entrance_record).exclude(id__in=ids)
        print booklet_details


    except Exception, exc:
        print exc
        has_error = True
        error_no = 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, entrance=entrance_record,
             has_error=has_error, error_no=error_no, packages=packages, booklet_details=booklet_details,
             minnersel=inner_menu_selected, menuinner=entrance_menus)
    return render_to_response("admin/de_entrance/tag_packages_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_entrance_publish', raise_exception=True)
def entrance_tag_package_publish(request, pk, bd_id):
    try:
        entrance = Entrance.objects.get(pk=pk)
        booklet_detail = EntranceBookletDetail.objects.prefetch_related('lesson').get(booklet__entrance=entrance, pk=bd_id)

        _ = EntranceTagSaleData.objects.get(entrance_type=entrance.entrance_type,
                                                    year=entrance.year,
                                                    month=entrance.month)

        # get entrance tag package
        tag_package = EntranceLessonTagPackage.objects.filter(booklet_detail=booklet_detail).first()
        if tag_package is None:
            data = create_entrance_tag_package(entrance, booklet_detail)
            data_json = json.dumps(data)
            package = EntranceLessonTagPackage(booklet_detail=booklet_detail,
                                               content=data_json,
                                               q_count=booklet_detail.q_count,
                                               is_changed=False)
            package.save()

            create_concough_activity(CONCOUGH_LOG_TYPES_2[3], booklet_detail)
        else:
            if tag_package.is_changed == True:
                data = create_entrance_tag_package(entrance, booklet_detail)
                data_json = json.dumps(data)

                tag_package.content = data_json
                tag_package.is_changed = False
                tag_package.save()

                create_concough_activity(CONCOUGH_LOG_TYPES_2[3], booklet_detail)

    except Exception, exc:
        pass

    return redirect("admin.de_entrance.tags.packages.list", pk=pk)


def create_entrance_tag_package(entrance, booklet_detail):
    data = {"entrance.unique_key": entrance.unique_key.get_hex(),
            "entrance.booklet_detail": {
                "remote_id": booklet_detail.id,
                "lesson.title": booklet_detail.lesson.title,
                "lesson.full_title": booklet_detail.lesson.full_title,
                "q_from": booklet_detail.q_from,
                "q_to": booklet_detail.q_to,
                "q_count": booklet_detail.q_count
            },
            "data": [],
            "tags": [],
            }

    tags = {}

    questions = EntranceQuestion.objects.prefetch_related('tags').filter(booklet_detail=booklet_detail)
    for question in questions:
        obj = {"q_no": question.question_number,
               "q_r_id": question.id,
               "tags": []}

        for tag in question.tags.all():
            obj["tags"].append(tag.id)
            tags[tag.id] = tag.title

        data["data"].append(obj)

    for item in tags.items():
        data["tags"].append({"t_id": item[0], "t_title": item[1]})

    return data


@login_required
@group_permission_required('main.de_entrance_publish', raise_exception=True)
def entrance_tag_package_del(request, pk, p_id):
    try:
        package = EntranceLessonTagPackage.objects.get(pk=p_id, booklet_detail__booklet__entrance__id=pk)
        package.delete()
    except:
        pass

    return redirect("admin.de_entrance.tags.packages.list", pk=pk)

