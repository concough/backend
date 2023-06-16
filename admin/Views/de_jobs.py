# coding=utf-8
from __future__ import division
import base64
import copy
import uuid, time

from datetime import datetime

import pymongo
import pytz
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.encoding import force_text
from gridfs import GridFS

from admin.Forms.DEJobForms import JobTaskAddTypistForm, JobTaskUploadTermForm, JobTaskCheckDoneForm, \
    JobTaskFinalPriceForm, JobTaskEntranceRejectForm, RejectReasonChoices, JobTaskEntrancePayOffForm, \
    UserCheckerEntranceCostAddForm
from admin.Helpers import menu_settings, jobs_menu_settings
from api.helpers.sms_handlers import sendSMS, sendSMS2
from digikunkor import settings
from main.Helpers.decorators import group_permission_required
from main.models import UserFinanialInformation, EntranceEditorFinanialPayment, UserCheckerState, \
    UserCheckerEntranceCost, EntranceCheckerFinanialPayment, StaffUserRate
from main.models_functions import connectToMongo


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_list(request):
    menu_selected = "jobs"
    inner_menu_selected = "entrance_jobs_list"

    user_group_name = None
    jobs = None
    form = None
    form2 = None
    form3 = None
    version = 0
    seen_count = 0
    check_final_cost = 0
    checker_state = "FULL"

    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1
    per_page = 20

    # get user group name
    user_group_names = request.user.groups.all()
    jobs_list = None

    # connect('mt1', host='192.168.0.21', port=27017, username='test3', password='test')
    db = connectToMongo()
    if 'master_operator' in [grp.name for grp in user_group_names] or 'administrator' in [grp.name for grp in
                                                                                          user_group_names]:
        jobs_list = db.job.find({'$and': [{'status': {'$ne': "FINISHED"}}, {'job_type': "ENTRANCE"}]}).sort(
            [('updated', -1), ('created', -1)]).skip((page - 1) * per_page).limit(per_page)
        # jobs_list = Job.objects(Q(status__ne="FINISHED") & Q(job_type="ENTRANCE"))
        user_group_name = 'master_operator'

    elif 'job_supervisor' in [grp.name for grp in user_group_names]:

        jobs_list = db.job.find({'$and': [{'status': {'$ne': "FINISHED"}}, {'job_type': "ENTRANCE"},
                                          {'job_owner_id': request.user.id}]}).sort(
            [('updated', -1), ('created', -1)]).skip((page - 1) * per_page).limit(per_page)
        # jobs_list = Job.objects(Q(status__ne="FINISHED") & Q(job_type="ENTRANCE"))
        user_group_name = 'job_supervisor'

    elif 'editor' in [grp.name for grp in user_group_names]:
        jobs_list = db.job.find({'data.tasks.main_editor.user_id': request.user.id}).sort('updated', -1).skip(
            (page - 1) * per_page).limit(per_page)
        # jobs_list = Job.objects(Q(data__tasks__state__in=("WAIT_FOR_TYPE", "TYPE_STARTED", "WAIT_FOR_CHECK", "TYPE_DONE", "REJECTED")) &
        #                         Q(data__tasks__main_editor__user_id=request.user.id)).order_by('-data.tasks.updated').order_by('-data.tasks.created')[(page - 1)* per_page: page * per_page]

        seen_count = EntranceEditorFinanialPayment.objects.filter(seen=False).count()
        user_group_name = 'editor'
        form = JobTaskUploadTermForm()

    elif 'check_in' in [grp.name for grp in user_group_names]:
        version = 1
        jobs_list_temp = db.job.find({'data.tasks.holding_editor.user_id': request.user.id}).sort(
            [("created", pymongo.ASCENDING), ("updated", pymongo.ASCENDING)])
        jobs_list = []
        for job in jobs_list_temp:
            tasks = job["data"]["tasks"]
            for task in tasks:
                if (task["state"] == "CHECK_STARTED" or task["state"] == "CHECK2_STARTED") and task["holding_editor"][
                    "user_id"] == request.user.id:

                    uf = UserFinanialInformation.objects.filter(user=request.user).first()
                    if uf:
                        cost_per = UserCheckerEntranceCost.objects.get(title=task["ftype"])
                        check_final_cost = (int(task["q_count"] * cost_per.cost * cost_per.rate / 100) + 1) * 100

                    jobs_list.append(job)
                    break

        if len(jobs_list) > 5:
            jobs_list = jobs_list[:5]

        if len(jobs_list) == 0:
            version = 2

            checker = UserCheckerState.objects.filter(user=request.user).first()
            if checker is not None:
                if checker.state == "SINGLE":
                    checker_state = "SINGLE"
                    jobs_list = db.job.find({'data.tasks.state': {'$in': ["WAIT_FOR_CHECK"]}}).sort(
                        [("created", pymongo.ASCENDING), ("updated", pymongo.ASCENDING)]).limit(5)
                else:
                    jobs_list = db.job.find({'data.tasks.state': {'$in': ["WAIT_FOR_CHECK", "CHECK_DONE"]}}).sort(
                        [("created", pymongo.ASCENDING), ("updated", pymongo.ASCENDING)]).limit(5)
            else:
                jobs_list = db.job.find({'data.tasks.state': {'$in': ["WAIT_FOR_CHECK", "CHECK_DONE"]}}).sort(
                    [("created", pymongo.ASCENDING), ("updated", pymongo.ASCENDING)]).limit(5)

        seen_count = EntranceCheckerFinanialPayment.objects.filter(seen=False).count()
        user_group_name = 'check_in'
        form2 = JobTaskCheckDoneForm()
        form3 = JobTaskEntranceRejectForm()
    else:
        # show forbidden message
        raise PermissionDenied

    d = dict(menul=menu_settings.menus, msel=menu_selected, jobs=jobs_list, ugn=user_group_name, checker_state=checker_state,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus, form=form, form2=form2,
             version=version, form3=form3, page=page + 1, seen_count=seen_count, check_final_cost=check_final_cost)
    return render_to_response("admin/de_jobs/entrance_job_list.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail(request, unique_id, detail_id=None):
    menu_selected = "jobs"
    inner_menu_selected = "entrance_jobs_list"

    job = None
    detail = None
    has_form_message = False
    form_message = -1
    form = None
    form2 = JobTaskFinalPriceForm()
    form3 = JobTaskEntranceRejectForm()
    log_level = 1

    typist_stat = {}

    user_group_names = request.user.groups.all()
    if 'master_operator' in [grp.name for grp in user_group_names] or 'administrator' in [grp.name for grp in
                                                                                          user_group_names]:
        log_level = 3
    if 'check_in' in [grp.name for grp in user_group_names]:
        log_level = 2

    try:
        db = connectToMongo()
        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id), 'job_owner_id': request.user.id})
        if 'master_operator' in [grp.name for grp in user_group_names] or 'administrator' in [grp.name for grp in
                                                                                              user_group_names]:
            job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id)})

        if job is None:
            return redirect('admin.de_jobs.entrance.list')

        if detail_id:
            for item in job["data"]["tasks"]:
                if item["task_unique_id"] == uuid.UUID(detail_id):
                    detail = item
                    break

        if request.method == "POST":
            form = JobTaskAddTypistForm(request.POST or None, files=request.FILES)

            if form.is_valid():
                job_unique_key = form.cleaned_data["job_unique_key"]
                task_unique_key = form.cleaned_data["task_unique_key"]
                price_per_q = int(form.cleaned_data["price_per_q"])
                typist = form.cleaned_data['typist']
                orig_file = form.cleaned_data['orig_file']
                file_type = form.cleaned_data['file_type']

                job = db.job.find_one({"job_relate_uniqueid": uuid.UUID(job_unique_key)})
                if job is not None and job["job_owner"]["user_id"] == request.user.id:
                    user = User.objects.get(username=typist)

                    must_rate = False
                    selected_task = None
                    for task in job["data"]["tasks"]:
                        if task["task_unique_id"] == uuid.UUID(task_unique_key):
                            selected_task = task
                            if "rejected_count" in task and task["rejected_count"] > 0:
                                must_rate = True

                    if must_rate:
                        # save rate
                        obj = {
                            "user_id": user.id,
                            "fullname": user.get_full_name(),
                            "username": user.username,
                            "total_rate": 0,
                            "total_count": 0,
                            "updated": datetime.now(tz=pytz.UTC),
                            "rates": []
                        }

                        user_rate_record = db.job_users_rate.find_one({'user_id': user.id})
                        if user_rate_record is None:
                            db.job_users_rate.insert_one(obj)
                            user_rate_record = obj

                        total_count = user_rate_record["total_count"] + 1
                        total_rate = ((user_rate_record["total_count"] * user_rate_record[
                            "total_rate"]) + 1) / total_count

                        db.job_users_rate.update_one({'user_id': user.id},
                                                     {"$set": {
                                                         "total_count": total_count,
                                                         "total_rate": total_rate,
                                                         "updated": datetime.now(tz=pytz.UTC)
                                                     },
                                                         "$push": {
                                                             "rates": {
                                                                 "job_type": "ENTRANCE",
                                                                 "rate": 1,
                                                                 "created": datetime.now(tz=pytz.UTC),
                                                                 "by": "system"
                                                             }
                                                         }})

                        rate_obj, created = StaffUserRate.objects.update_or_create(user=user, defaults={
                            'rate': total_rate,
                            'rate_count': total_count
                        })

                    editor = {
                        "user_id": user.id,
                        "username": user.username,
                        "fullname": user.get_full_name(),
                        "joined": user.date_joined
                    }

                    log = {
                        "log_type": "DEBUG",
                        "level": 1,
                        "title": "WAIT_FOR_TYPE",
                        "description": u"در انتظار تایپ توسط تایپیست (مدیر پنل: %s - %s)" % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                        "created": datetime.now(tz=pytz.UTC)
                    }

                    fs = GridFS(db)
                    if selected_task["orig_file"] is not None:
                        # must delete first
                        if fs.exists(selected_task["orig_file"]):
                            fs.delete(selected_task["orig_file"])

                    if "term_file" in selected_task and selected_task["term_file"] is not None:
                        if fs.exists(selected_task["term_file"]):
                            fs.delete(selected_task["term_file"])

                    if "main_term_file" in selected_task and selected_task["main_term_file"] is not None:
                        if fs.exists(selected_task["main_term_file"]):
                            fs.delete(selected_task["main_term_file"])

                    fs_obj = fs.put(orig_file, content_type='application/pdf')

                    db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key),
                                       'job_owner_id': request.user.id},
                                      {'$set': {"data.tasks.$.price_per_q": price_per_q,
                                                "data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                "updated": datetime.now(tz=pytz.UTC),
                                                "data.tasks.$.main_editor": editor,
                                                "status": "STARTED",
                                                "data.tasks.$.state": "WAIT_FOR_TYPE",
                                                "data.tasks.$.orig_file": fs_obj,
                                                "data.tasks.$.ftype": file_type,
                                                "data.tasks.$.rejected_count": 0
                                                },
                                       "$addToSet": {
                                           "data.tasks.$.logs": log
                                       }})

                    return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)
            else:
                has_form_message = True
                form_message = 1

        jobs_list = db.job.find({'$and': [{'status': {'$ne': "FINISHED"}}, {'job_type': "ENTRANCE"}]})

        for job1 in jobs_list:
            if job1["status"] == "STARTED":

                for task in job1["data"]["tasks"]:
                    if task["state"] != "CREATED":
                        user_username = task["main_editor"]["username"]

                        if not typist_stat.has_key(user_username):
                            print type(task["main_editor"]["joined"])

                            typist_stat[user_username] = {
                                "user_id": task["main_editor"]["user_id"],
                                "fullname": task["main_editor"]["fullname"],
                                "joined": task["main_editor"]["joined"],
                                "count": 0
                            }
                        if task["state"] == "WAIT_FOR_TYPE" or task["state"] == "TYPE_STARTED" or task[
                            "state"] == "REJECTED":
                            typist_stat[user_username]["count"] += 1

        form = JobTaskAddTypistForm()


    except Exception, exc:
        print exc
        return redirect('admin.de_jobs.entrance.detail', unique_id=unique_id)

    d = dict(menul=menu_settings.menus, msel=menu_selected, job=job, form=form, log_level=log_level,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus, detail=detail, form2=form2,
             form3=form3, typist_stat=typist_stat)

    return render_to_response("admin/de_jobs/entrance_job_detail.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_finish(request, unique_id):
    try:
        db = connectToMongo()
        record = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'job_owner_id': request.user.id})

        can_finish = True
        if record:
            for task in record["data"]["tasks"]:
                if task["state"] != "CREATED" and task["state"] != "PAYED":
                    can_finish = False
                    break

            if can_finish:
                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'job_owner_id': request.user.id},
                              {'$set': {"status": "FINISHED",
                                        }
                               })
                return redirect("admin.de_jobs.entrance.list")

    except Exception, exc:
        print exc


    return redirect('admin.de_jobs.entrance.detail', unique_id=unique_id)


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_choose_typist(request):
    try:
        db = connectToMongo()

        if request.method == "POST":
            form = JobTaskAddTypistForm(request.POST or None, files=request.FILES)

            if form.is_valid():
                job_unique_key = form.cleaned_data["job_unique_key"]
                task_unique_key = form.cleaned_data["task_unique_key"]
                price_per_q = int(form.cleaned_data["price_per_q"])
                typist = form.cleaned_data['typist']
                orig_file = form.cleaned_data['orig_file']
                file_type = form.cleaned_data['file_type']

                job = db.job.find_one({"job_relate_uniqueid": uuid.UUID(job_unique_key)})
                if job is not None and job["job_owner"]["user_id"] == request.user.id:
                    user = User.objects.get(username=typist)

                    must_rate = False
                    selected_task = None
                    for task in job["data"]["tasks"]:
                        if task["task_unique_id"] == uuid.UUID(task_unique_key):
                            selected_task = task
                            if task["rejected_count"] > 0:
                                must_rate = True

                    if must_rate:
                        # save rate
                        obj = {
                            "user_id": user.id,
                            "fullname": user.get_full_name(),
                            "username": user.username,
                            "total_rate": 0,
                            "total_count": 0,
                            "updated": datetime.now(tz=pytz.UTC),
                            "rates": []
                        }

                        user_rate_record = db.job_users_rate.find_one({'user_id': user.id})
                        if user_rate_record is None:
                            db.job_users_rate.insert_one(obj)
                            user_rate_record = obj

                        total_count = user_rate_record["total_count"] + 1
                        total_rate = ((user_rate_record["total_count"] * user_rate_record[
                            "total_rate"]) + 1) / total_count

                        db.job_users_rate.update_one({'user_id': user.id},
                                                     {"$set": {
                                                         "total_count": total_count,
                                                         "total_rate": total_rate,
                                                         "updated": datetime.now(tz=pytz.UTC)
                                                     },
                                                         "$push": {
                                                             "rates": {
                                                                 "job_type": "ENTRANCE",
                                                                 "rate": 1,
                                                                 "created": datetime.now(tz=pytz.UTC),
                                                                 "by": "system"
                                                             }
                                                         }})

                        rate_obj, created = StaffUserRate.objects.update_or_create(user=user, defaults={
                            'rate': total_rate,
                            'rate_count': total_count
                        })

                    editor = {
                        "user_id": user.id,
                        "username": user.username,
                        "fullname": user.get_full_name(),
                        "joined": user.date_joined
                    }

                    log = {
                        "log_type": "DEBUG",
                        "level": 1,
                        "title": "WAIT_FOR_TYPE",
                        "description": u"در انتظار تایپ توسط تایپیست (مدیر پنل: %s - %s)" % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                        "created": datetime.now(tz=pytz.UTC)
                    }

                    fs = GridFS(db)
                    if selected_task["orig_file"] is not None:
                        # must delete first
                        if fs.exists(selected_task["orig_file"]):
                            fs.delete(selected_task["orig_file"])

                    if "term_file" in selected_task and selected_task["term_file"] is not None:
                        if fs.exists(selected_task["term_file"]):
                            fs.delete(selected_task["term_file"])

                    if "main_term_file" in selected_task and selected_task["main_term_file"] is not None:
                        if fs.exists(selected_task["main_term_file"]):
                            fs.delete(selected_task["main_term_file"])

                    fs_obj = fs.put(orig_file, content_type='application/pdf')

                    db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key),
                                       "job_owner_id": request.user.id},
                                      {'$set': {"data.tasks.$.price_per_q": price_per_q,
                                                "data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                "updated": datetime.now(tz=pytz.UTC),
                                                "data.tasks.$.main_editor": editor,
                                                "status": "STARTED",
                                                "data.tasks.$.state": "WAIT_FOR_TYPE",
                                                "data.tasks.$.orig_file": fs_obj,
                                                "data.tasks.$.ftype": file_type,
                                                "data.tasks.$.rejected_count": 0
                                                },
                                       "$addToSet": {
                                           "data.tasks.$.logs": log
                                       }})

                # return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)

    except Exception, exc:
        print exc
        # return redirect('admin.de_jobs.entrance.detail', unique_id=unique_id)

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_cancel_type(request, unique_id, detail_id):
    try:
        db = connectToMongo()
        job = db.job.find_one({"job_relate_uniqueid": uuid.UUID(unique_id)})

        log = {
            "log_type": "DEBUG",
            "level": 1,
            "title": "CREATED",
            "description": u"تایپ توسط مدیر پنل (%s - %s) کنسل شد." % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
            "created": datetime.now(tz=pytz.UTC)
        }

        if job is not None:

            selected_task = None
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    selected_task = task

            fs = GridFS(db)

            if "orig_file" in selected_task and selected_task["orig_file"] is not None:
                if fs.exists(selected_task["orig_file"]):
                    fs.delete(selected_task["orig_file"])

            if "term_file" in selected_task and selected_task["term_file"] is not None:
                if fs.exists(selected_task["term_file"]):
                    fs.delete(selected_task["term_file"])

            if "main_term_file" in selected_task and selected_task["main_term_file"] is not None:
                if fs.exists(selected_task["main_term_file"]):
                    fs.delete(selected_task["main_term_file"])

            db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               "job_owner_id": request.user.id},
                              {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                        "updated": datetime.now(tz=pytz.UTC),
                                        "data.tasks.$.main_editor": None,
                                        "data.tasks.$.holding_editor": None,
                                        "data.tasks.$.state": "CREATED",
                                        "data.tasks.$.orig_file": None,
                                        "data.tasks.$.ftype": None,
                                        "data.tasks.$.rejected_count": 0,
                                        "data.tasks.$.price_per_q": 0
                                        },
                               "$addToSet": {
                                   "data.tasks.$.logs": log
                               }})

                # return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)

    except Exception, exc:
        print exc
        # return redirect('admin.de_jobs.entrance.detail', unique_id=unique_id)

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_start_type(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        user = request.user
        holding = {
            "user_id": user.id,
            "username": user.username,
            "fullname": user.get_full_name(),
            "joined": user.date_joined
        }

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               'data.tasks.main_editor.user_id': request.user.id})

        start_type = "wait"
        for task in job["data"]["tasks"]:
            if task["task_unique_id"] == uuid.UUID(detail_id):
                if task["state"] == "REJECTED":
                    start_type = "rejected"
                    break

        if start_type == 'wait':
            log = {
                "log_type": "INFO",
                "level": 1,
                "title": "TYPE_STARTED",
                "description": u"تایپ توسط %s - %s تایپیست شروع شده است." % (user.get_full_name(), user.username),
                "created": datetime.now(tz=pytz.UTC)
            }

            db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               'data.tasks.main_editor.user_id': request.user.id,
                               'data.tasks.state': "WAIT_FOR_TYPE"},
                              {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                        "updated": datetime.now(tz=pytz.UTC),
                                        "data.tasks.$.holding_editor": holding,
                                        "status": "STARTED",
                                        "data.tasks.$.state": "TYPE_STARTED"
                                        },
                               "$addToSet": {
                                   "data.tasks.$.logs": log
                               }})
        elif start_type == 'rejected':
            log = {
                "log_type": "INFO",
                "level": 1,
                "title": "TYPE_STARTED",
                "description": u"اصلاح تایپ توسط %s تایپیست شروع شده است." % user.get_full_name(),
                "created": datetime.now(tz=pytz.UTC)
            }

            db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               'data.tasks.main_editor.user_id': request.user.id,
                               'data.tasks.state': "REJECTED"},
                              {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                        "updated": datetime.now(tz=pytz.UTC),
                                        "data.tasks.$.holding_editor": holding,
                                        "status": "STARTED",
                                        "data.tasks.$.state": "TYPE_STARTED"
                                        },
                               "$addToSet": {
                                   "data.tasks.$.logs": log
                               }})

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_type_upload_file(request):
    try:
        db = connectToMongo()
        user = request.user

        if request.method == "POST":
            form = JobTaskUploadTermForm(request.POST or None, files=request.FILES)

            if form.is_valid():
                job_unique_key = form.cleaned_data["job_unique_key"]
                task_unique_key = form.cleaned_data["task_unique_key"]
                term_file = form.cleaned_data['term_file']

                holding = {
                    "user_id": user.id,
                    "username": user.username,
                    "fullname": user.get_full_name(),
                    "joined": user.date_joined
                }

                job = db.job.find_one({"job_relate_uniqueid": uuid.UUID(job_unique_key)})
                if job is not None:

                    selected_task = None
                    for task in job["data"]["tasks"]:
                        if task["task_unique_id"] == uuid.UUID(task_unique_key):
                            selected_task = task

                    fs = GridFS(db)

                    if "term_file" in selected_task and selected_task["term_file"] is not None:
                        if fs.exists(selected_task["term_file"]):
                            fs.delete(selected_task["term_file"])

                    if "main_term_file" in selected_task and selected_task["main_term_file"] is not None:
                        if fs.exists(selected_task["main_term_file"]):
                            fs.delete(selected_task["main_term_file"])

                    fs_obj = fs.put(term_file,
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

                    term_file.seek(0)

                    fs_obj1 = fs.put(term_file,
                                     content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

                    db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key),
                                       'data.tasks.main_editor.user_id': request.user.id,
                                       'data.tasks.state': "TYPE_STARTED"},
                                      {'$set': {"data.tasks.$.holding_editor": holding,
                                                "data.tasks.$.term_file": fs_obj,
                                                "data.tasks.$.main_term_file": fs_obj1
                                                }
                                       })

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_type_done(request, unique_id, detail_id):
    try:
        db = connectToMongo()
        user = request.user

        can_done = False
        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id)})
        if job is not None:
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    if task["main_editor"]["user_id"] == request.user.id:
                        if task["main_term_file"] is not None:
                            can_done = True

        if can_done:
            holding = {
                "user_id": user.id,
                "username": user.username,
                "fullname": user.get_full_name(),
                "joined": user.date_joined
            }

            log = {
                "log_type": "INFO",
                "level": 1,
                "title": "TYPE_DONE",
                "description": u"تایپ توسط %s - %s (تایپیست) به اتمام رسید." % (user.get_full_name(), user.username),
                "created": datetime.now(tz=pytz.UTC)
            }

            db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               'data.tasks.main_editor.user_id': request.user.id,
                               'data.tasks.state': "TYPE_STARTED"},
                              {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                        "updated": datetime.now(tz=pytz.UTC),
                                        "data.tasks.$.holding_editor": holding,
                                        "status": "STARTED",
                                        "data.tasks.$.state": "TYPE_DONE"
                                        },
                               "$addToSet": {
                                   "data.tasks.$.logs": log
                               }})

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_download_main_file(request, unique_id):
    user = request.user
    user_group_names = request.user.groups.all()

    can_download = False

    try:
        db = connectToMongo()
        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id)})

        filename = ""
        if 'administrator' in [grp.name for grp in user_group_names] or 'master_operator' in [grp.name for grp in
                                                                                              user_group_names]:
            can_download = True
            filename = u"%s-%s - %s - %s (%s) - %s - " % (
                job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
                job["data"]["group"], job["data"]["organization"])

            filename = filename.encode('utf-8')

        elif 'job_supervisor' in [grp.name for grp in user_group_names]:
            if job["job_owner"]["user_id"] == request.user.id:
                can_download = True
                filename = u"%s-%s - %s - %s (%s) - %s - " % (
                    job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
                    job["data"]["group"], job["data"]["organization"])

                filename = filename.encode('utf-8')

        if can_download:
            fs = GridFS(db)
            fs_obj = fs.get(job["job_main_file"])
            data = fs_obj.read()

            response = HttpResponse(content=data)
            response['Content-Type'] = fs_obj.content_type
            response['Content-Disposition'] = 'attachment; filename="%s.%s"' \
                                              % (filename, "zip")
            return response

    except Exception, exc:
        print exc

    return HttpResponse(status=404)

@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_download_orig_file(request, unique_id, detail_id):
    user = request.user
    user_group_names = request.user.groups.all()

    can_download = False

    try:
        db = connectToMongo()
        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id)})

        filename = ""
        if 'administrator' in [grp.name for grp in user_group_names] or 'master_operator' in [grp.name for grp in
                                                                                              user_group_names]:
            can_download = True
            filename = u"%s-%s - %s - %s (%s) - %s - " % (
                job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
                job["data"]["group"], job["data"]["organization"])

            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    filename += task["lesson_title"]
                    filename = filename.encode('utf-8')

        elif 'job_supervisor' in [grp.name for grp in user_group_names]:
            if job["job_owner"]["user_id"] == request.user.id:
                can_download = True
                filename = u"%s-%s - %s - %s (%s) - %s - " % (
                    job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
                    job["data"]["group"], job["data"]["organization"])

                for task in job["data"]["tasks"]:
                    if task["task_unique_id"] == uuid.UUID(detail_id):
                        filename += task["lesson_title"]
                        filename = filename.encode('utf-8')

        elif 'check_in' in [grp.name for grp in user_group_names]:
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id) and (
                                task["state"] == "CHECK_STARTED" and task["holding_editor"][
                            "user_id"] == request.user.id) or \
                        (task["state"] == "CHECK2_STARTED" and task["holding_editor"]["user_id"] == request.user.id):
                    can_download = True
                    filename = task["task_unique_id"]

        elif 'editor' in [grp.name for grp in user_group_names]:
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id) and task["state"] == "TYPE_STARTED" and \
                                task["holding_editor"]["user_id"] == request.user.id:
                    can_download = True
                    filename = task["task_unique_id"]

        if can_download:
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    fs = GridFS(db)
                    fs_obj = fs.get(task["orig_file"])
                    data = fs_obj.read()

                    response = HttpResponse(content=data)
                    response['Content-Type'] = 'application/pdf'
                    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' \
                                                      % filename
                    return response


    except Exception, exc:
        print exc

    return HttpResponse(status=404)


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_download_term_file(request, unique_id, detail_id):
    user = request.user
    user_group_names = request.user.groups.all()

    can_download = False

    db = connectToMongo()
    job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id)})

    filename = ""
    if 'administrator' in [grp.name for grp in user_group_names] or 'master_operator' in [grp.name for grp in
                                                                                          user_group_names]:
        can_download = True
        filename = u"%s-%s - %s - %s (%s) - %s - " % (
            job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
            job["data"]["group"], job["data"]["organization"])

        for task in job["data"]["tasks"]:
            if task["task_unique_id"] == uuid.UUID(detail_id):
                filename += task["lesson_title"]
                filename = filename.encode('utf-8')

    elif 'job_supervisor' in [grp.name for grp in user_group_names]:
        if job["job_owner"]["user_id"] == request.user.id:
            can_download = True
            filename = u"%s-%s - %s - %s (%s) - %s - " % (
                job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
                job["data"]["group"], job["data"]["organization"])

            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    filename += task["lesson_title"]
                    filename = filename.encode('utf-8')

    elif 'check_in' in [grp.name for grp in user_group_names]:
        for task in job["data"]["tasks"]:
            if task["task_unique_id"] == uuid.UUID(detail_id) and (
                            task["state"] == "CHECK_STARTED" or task["state"] == "CHECK2_STARTED"):
                can_download = True
                filename = task["task_unique_id"]

    if can_download:
        try:

            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    fs = GridFS(db)
                    fs_obj = fs.get(task["term_file"])
                    data = fs_obj.read()

                    response = HttpResponse(content=data)
                    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    response['Content-Disposition'] = 'attachment; filename="%s.docx"' \
                                                      % filename
                    return response

        except Exception, exc:
            print exc

    return HttpResponse(status=404)



@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_download_main_term_file(request, unique_id, detail_id):
    user = request.user
    user_group_names = request.user.groups.all()

    can_download = False

    db = connectToMongo()
    job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id)})

    filename = ""
    if 'administrator' in [grp.name for grp in user_group_names] or 'master_operator' in [grp.name for grp in
                                                                                          user_group_names]:
        can_download = True
        filename = u"%s-%s - %s - %s (%s) - %s - " % (
            job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
            job["data"]["group"], job["data"]["organization"])

        for task in job["data"]["tasks"]:
            if task["task_unique_id"] == uuid.UUID(detail_id):
                filename += task["lesson_title"]
                filename = filename.encode('utf-8')

    elif 'job_supervisor' in [grp.name for grp in user_group_names]:
        if job["job_owner"]["user_id"] == request.user.id:
            can_download = True
            filename = u"%s-%s - %s - %s (%s) - %s - " % (
                job["data"]["year"], job["data"]["month"], job["data"]["type"], job["data"]["set"],
                job["data"]["group"], job["data"]["organization"])

            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    filename += task["lesson_title"]
                    filename = filename.encode('utf-8')

    elif 'editor' in [grp.name for grp in user_group_names]:
        for task in job["data"]["tasks"]:
            if task["task_unique_id"] == uuid.UUID(detail_id) and (
                            task["state"] == "TYPE_STARTED" or task["main_editor"]["user_id"] == user.id):
                can_download = True
                filename = task["task_unique_id"]

    if can_download:
        try:

            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    fs = GridFS(db)
                    fs_obj = fs.get(task["main_term_file"])
                    data = fs_obj.read()

                    response = HttpResponse(content=data)
                    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    response['Content-Disposition'] = 'attachment; filename="%s.docx"' \
                                                      % filename
                    return response

        except Exception, exc:
            print exc

    return HttpResponse(status=404)


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_wait_for_check(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id),
                           'data.tasks.state': "TYPE_DONE",
                           'job_owner_id': request.user.id})

        if job:
            if job["job_owner_id"] == request.user.id:
                log = {
                    "log_type": "DEBUG",
                    "level": 1,
                    "title": "WAIT_FOR_CHECK",
                    "description": u"در انتظار بررسی توسط بررسی کنندگان (مدیر پنل: %s - %s)" % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                    "created": datetime.now(tz=pytz.UTC)
                }

                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                   'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                   'data.tasks.state': "TYPE_DONE",
                                   'job_owner_id': request.user.id},
                                  {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                            "updated": datetime.now(tz=pytz.UTC),
                                            "status": "STARTED",
                                            "data.tasks.$.state": "WAIT_FOR_CHECK"
                                            },
                                   "$addToSet": {
                                       "data.tasks.$.logs": log
                                   }})

    except Exception, exc:
        print exc

    return redirect(request.META['HTTP_REFERER'])
    # return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_wait_for_recheck(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               'data.tasks.state': "TYPE_DONE",
                               'job_owner_id': request.user.id})

        if job:
            if job["job_owner_id"] == request.user.id:

                log = {
                    "log_type": "DEBUG",
                    "level": 1,
                    "title": "WAIT_FOR_RECHECK",
                    "description": u"در انتظار بررسی مجدد توسط بررسی کنندگان (مدیر پنل: %s - %s)" % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                    "created": datetime.now(tz=pytz.UTC)
                }

                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                   'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                   'data.tasks.state': "ACCEPTED",
                                   'job_owner_id': request.user.id},
                                  {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                            "updated": datetime.now(tz=pytz.UTC),
                                            "status": "STARTED",
                                            "data.tasks.$.state": "CHECK_DONE"
                                            },
                                   "$addToSet": {
                                       "data.tasks.$.logs": log
                                   }})

    except Exception, exc:
        print exc

    # return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)
    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_reject_and_retype(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id),
                           'data.tasks.state': "WAIT_FOR_REJECTED",
                           'job_owner_id': request.user.id})

        if job is not None:
            if job["status"] == "STARTED":
                for task in job["data"]["tasks"]:
                    if task["task_unique_id"] == uuid.UUID(detail_id):
                        if "check_state" in task and "checkers" in task:
                            rejected = 0
                            if "check_state" in task and "checkers" in task:
                                rejected = task["check_state"]

                            if rejected == 2:
                                user_id = task["checkers"][1]["user_id"]
                                uf = UserFinanialInformation.objects.filter(user__id=user_id).first()

                                if uf:
                                    cost_per = UserCheckerEntranceCost.objects.get(title=task["ftype"])

                                    final_cost = (int(task["q_count"] * cost_per.cost * cost_per.rate * 0.1 / 10) + 1) * 10

                                    task_detail = {
                                        "task_unique_id": task["task_unique_id"],
                                        "job_unique_id": job["job_relate_uniqueid"],
                                        "total_cost": final_cost,
                                        "job_type": job["job_type"],
                                        "check_state": "REJECT",
                                        "created": datetime.now(tz=pytz.UTC)

                                    }

                                    obj = {
                                        "user_id": user_id,
                                        "user_fullname": task["checkers"][1]["fullname"],
                                        "user_username": task["checkers"][1]["username"],
                                        "user_date_joined": task["checkers"][1]["joined"],
                                        "user_type": "CHECK_IN",
                                        "task_detail": [],
                                        "finance_detail": {
                                            "shaba": uf.bank_shaba,
                                            "bank_name": uf.bank_name
                                        }
                                    }

                                    job_finance_record = db.job_finance.find_one({'user_id': user_id})
                                    if job_finance_record is None:
                                        db.job_finance.insert_one(obj)

                                    db.job_finance.update_one({'user_id': user_id},
                                                              {"$addToSet": {
                                                                  "task_detail": task_detail
                                                              }})

                                # save rate
                                obj = {
                                    "user_id": user_id,
                                    "fullname": task["checkers"][1]["fullname"],
                                    "username": task["checkers"][1]["username"],
                                    "total_rate": 0,
                                    "total_count": 0,
                                    "updated": datetime.now(tz=pytz.UTC),
                                    "rates": []
                                }

                                user_rate_record = db.job_users_rate.find_one({'user_id': user_id})
                                if user_rate_record is None:
                                    db.job_users_rate.insert_one(obj)
                                    user_rate_record = obj

                                total_count = user_rate_record["total_count"] + 1
                                total_rate = ((user_rate_record["total_count"] * user_rate_record["total_rate"]) + 5) / total_count

                                db.job_users_rate.update_one({'user_id': user_id},
                                                          {"$set": {
                                                            "total_count": total_count,
                                                              "total_rate": total_rate,
                                                              "updated": datetime.now(tz=pytz.UTC)
                                                          },
                                                          "$push": {
                                                              "rates": {
                                                                  "job_type": "ENTRANCE",
                                                                  "rate": 5,
                                                                  "created": datetime.now(tz=pytz.UTC),
                                                                  "by": "system"
                                                              }
                                                          }})

                                rate_user = User.objects.get(pk=user_id)
                                rate_obj, created = StaffUserRate.objects.update_or_create(user=rate_user, defaults={
                                    'rate': total_rate,
                                    'rate_count': total_count
                                })

                                user_id = task["checkers"][0]["user_id"]
                                uf = UserFinanialInformation.objects.filter(user__id=user_id).first()

                                if uf:
                                    cost_per = UserCheckerEntranceCost.objects.get(title=task["ftype"])

                                    final_cost = (int(task["q_count"] * cost_per.cost * cost_per.rate * 0.1 / 10) - 1) * 10 * -2

                                    task_detail = {
                                        "task_unique_id": task["task_unique_id"],
                                        "job_unique_id": job["job_relate_uniqueid"],
                                        "total_cost": final_cost,
                                        "job_type": job["job_type"],
                                        "check_state": "W-REJECT",
                                        "created": datetime.now(tz=pytz.UTC)

                                    }

                                    obj = {
                                        "user_id": user_id,
                                        "user_fullname": task["checkers"][0]["fullname"],
                                        "user_username": task["checkers"][0]["username"],
                                        "user_date_joined": task["checkers"][0]["joined"],
                                        "user_type": "CHECK_IN",
                                        "task_detail": [],
                                        "finance_detail": {
                                            "shaba": uf.bank_shaba,
                                            "bank_name": uf.bank_name
                                        }
                                    }

                                    job_finance_record = db.job_finance.find_one({'user_id': user_id})
                                    if job_finance_record is None:
                                        db.job_finance.insert_one(obj)

                                    db.job_finance.update_one({'user_id': user_id},
                                                              {"$addToSet": {
                                                                  "task_detail": task_detail
                                                              }})

                                # save rate
                                obj = {
                                    "user_id": user_id,
                                    "fullname": task["checkers"][0]["fullname"],
                                    "username": task["checkers"][0]["username"],
                                    "total_rate": 0,
                                    "total_count": 0,
                                    "updated": datetime.now(tz=pytz.UTC),
                                    "rates": []
                                }

                                user_rate_record = db.job_users_rate.find_one({'user_id': user_id})
                                if user_rate_record is None:
                                    db.job_users_rate.insert_one(obj)
                                    user_rate_record = obj

                                total_count = user_rate_record["total_count"] + 1
                                total_rate = ((user_rate_record["total_count"] * user_rate_record[
                                    "total_rate"]) + 3) / total_count

                                db.job_users_rate.update_one({'user_id': user_id},
                                                             {"$set": {
                                                                 "total_count": total_count,
                                                                 "total_rate": total_rate,
                                                                 "updated": datetime.now(tz=pytz.UTC)
                                                             },
                                                                 "$push": {
                                                                     "rates": {
                                                                         "job_type": "ENTRANCE",
                                                                         "rate": 3,
                                                                         "created": datetime.now(tz=pytz.UTC),
                                                                         "by": "system"
                                                                     }
                                                                 }})

                                rate_user = User.objects.get(pk=user_id)
                                rate_obj, created = StaffUserRate.objects.update_or_create(user=rate_user, defaults={
                                    'rate': total_rate,
                                    'rate_count': total_count
                                })

                            elif rejected == 1:
                                user_id = task["checkers"][0]["user_id"]
                                uf = UserFinanialInformation.objects.filter(user__id=user_id).first()

                                if uf:
                                    cost_per = UserCheckerEntranceCost.objects.get(title=task["ftype"])

                                    final_cost = (int(task["q_count"] * cost_per.cost * cost_per.rate * 0.1 / 10) + 1) * 10

                                    task_detail = {
                                        "task_unique_id": task["task_unique_id"],
                                        "job_unique_id": job["job_relate_uniqueid"],
                                        "total_cost": final_cost,
                                        "job_type": job["job_type"],
                                        "check_state": "REJECT",
                                        "created": datetime.now(tz=pytz.UTC)

                                    }

                                    obj = {
                                        "user_id": user_id,
                                        "user_fullname": task["checkers"][0]["fullname"],
                                        "user_username": task["checkers"][0]["username"],
                                        "user_date_joined": task["checkers"][0]["joined"],
                                        "user_type": "CHECK_IN",
                                        "task_detail": [],
                                        "finance_detail": {
                                            "shaba": uf.bank_shaba,
                                            "bank_name": uf.bank_name
                                        }
                                    }

                                    job_finance_record = db.job_finance.find_one({'user_id': user_id})
                                    if job_finance_record is None:
                                        db.job_finance.insert_one(obj)

                                    db.job_finance.update_one({'user_id': user_id},
                                                              {"$addToSet": {
                                                                  "task_detail": task_detail
                                                              }})

                                # save rate
                                obj = {
                                    "user_id": user_id,
                                    "fullname": task["checkers"][0]["fullname"],
                                    "username": task["checkers"][0]["username"],
                                    "total_rate": 0,
                                    "total_count": 0,
                                    "updated": datetime.now(tz=pytz.UTC),
                                    "rates": []
                                }

                                user_rate_record = db.job_users_rate.find_one({'user_id': user_id})
                                if user_rate_record is None:
                                    db.job_users_rate.insert_one(obj)
                                    user_rate_record = obj

                                total_count = user_rate_record["total_count"] + 1
                                total_rate = ((user_rate_record["total_count"] * user_rate_record["total_rate"]) + 5) / total_count

                                db.job_users_rate.update_one({'user_id': user_id},
                                                             {"$set": {
                                                                 "total_count": total_count,
                                                                 "total_rate": total_rate,
                                                                 "updated": datetime.now(tz=pytz.UTC)
                                                             },
                                                                 "$push": {
                                                                     "rates": {
                                                                         "job_type": "ENTRANCE",
                                                                         "rate": 5,
                                                                         "created": datetime.now(tz=pytz.UTC),
                                                                         "by": "system"
                                                                     }
                                                                 }})

                                rate_user = User.objects.get(pk=user_id)
                                rate_obj, created = StaffUserRate.objects.update_or_create(user=rate_user, defaults={
                                    'rate': total_rate,
                                    'rate_count': total_count
                                })


            log = {
                "log_type": "DEBUG",
                "level": 1,
                "title": "REJECTED",
                "description":  u"در انتظار اصلاحات توسط تایپیست (مدیر پنل %s -  %s)" % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                "created": datetime.now(tz=pytz.UTC)
            }

            rejected = 0
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    if "rejected_count" in task:
                        rejected = task["rejected_count"] + 1

            db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                               'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               'data.tasks.state': "WAIT_FOR_REJECTED",
                               'job_owner_id': request.user.id},
                              {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                        "updated": datetime.now(tz=pytz.UTC),
                                        "status": "STARTED",
                                        "data.tasks.$.state": "REJECTED",
                                        "data.tasks.$.main_term_file": None,
                                        "data.tasks.$.term_file": None,
                                        "data.tasks.$.rejected_count": rejected
                                        },
                               "$addToSet": {
                                   "data.tasks.$.logs": log
                               }})

    except Exception, exc:
        print exc

    # return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)
    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_send_for_finance(request):
    try:

        if request.method == "POST":
            form = JobTaskFinalPriceForm(request.POST or None)

            if form.is_valid():
                unique_id = form.cleaned_data["job_unique_key"]
                detail_id = form.cleaned_data["task_unique_key"]
                final_cost = form.cleaned_data['final_cost']

                db = connectToMongo()
                job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                       'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                       'job_owner_id': request.user.id})

                if job is not None and job["job_owner"]["user_id"] == request.user.id:
                    user_id = 0
                    selected_task = None
                    checkers = []
                    rejected_count = 0
                    for task in job["data"]["tasks"]:
                        if task["task_unique_id"] == uuid.UUID(detail_id):
                            selected_task = task
                            user_id = task["main_editor"]["user_id"]
                            checkers = task["checkers"]
                            if "rejected_count" in task:
                                rejected_count = task["rejected_count"]
                            break

                    if user_id > 0:
                        uf = UserFinanialInformation.objects.get(user__id=user_id)

                        job_data = copy.deepcopy(job["data"])
                        del job_data["tasks"]
                        job_data["lesson_title"] = selected_task["lesson_title"]

                        task_detail = {
                            "task_unique_id": selected_task["task_unique_id"],
                            "job_unique_id": job["job_relate_uniqueid"],
                            "total_cost": selected_task["q_count"] * final_cost,
                            "job_type": job["job_type"],
                            "job_detail": job_data,
                            "created": datetime.now(tz=pytz.UTC)
                        }

                        obj = {
                            "user_id": user_id,
                            "user_fullname": selected_task["main_editor"]["fullname"],
                            "user_username": selected_task["main_editor"]["username"],
                            "user_date_joined": selected_task["main_editor"]["joined"],
                            "user_type": "EDITOR",
                            "task_detail": [],
                            "finance_detail": {
                                "shaba": uf.bank_shaba,
                                "bank_name": uf.bank_name
                            }
                        }

                        job_finance_record = db.job_finance.find_one({'user_id': user_id})
                        if job_finance_record is None:
                            db.job_finance.insert_one(obj)

                        db.job_finance.update_one({'user_id': user_id},
                                                  {"$addToSet": {
                                                      "task_detail": task_detail
                                                  }})

                        log = {
                            "log_type": "INFO",
                            "level": 1,
                            "title": "SEND_FOR_FINANCE",
                            "description": u"در انتظار پرداخت مالی (مدیر پنل: %s - %s)" % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                            "created": datetime.now(tz=pytz.UTC)
                        }

                        db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                           'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                           'data.tasks.state': "ACCEPTED",
                                           'job_owner_id': request.user.id},
                                          {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                    "updated": datetime.now(tz=pytz.UTC),
                                                    "status": "STARTED",
                                                    "data.tasks.$.state": "SEND_FOR_FINANCE",
                                                    "data.tasks.$.price_per_q_final": final_cost
                                                    },
                                           "$addToSet": {
                                               "data.tasks.$.logs": log
                                           }})

                        # save rate
                        obj = {
                            "user_id": user_id,
                            "fullname": selected_task["main_editor"]["fullname"],
                            "username": selected_task["main_editor"]["username"],
                            "total_rate": 0,
                            "total_count": 0,
                            "updated": datetime.now(tz=pytz.UTC),
                            "rates": []
                        }

                        user_rate_record = db.job_users_rate.find_one({'user_id': user_id})
                        if user_rate_record is None:
                            db.job_users_rate.insert_one(obj)
                            user_rate_record = obj

                        current_rate = 5 - (rejected_count * 0.7)

                        total_count = user_rate_record["total_count"] + 1
                        total_rate = ((user_rate_record["total_count"] * user_rate_record[
                            "total_rate"]) + current_rate) / total_count

                        db.job_users_rate.update_one({'user_id': user_id},
                                                     {"$set": {
                                                         "total_count": total_count,
                                                         "total_rate": total_rate,
                                                         "updated": datetime.now(tz=pytz.UTC)
                                                     },
                                                         "$push": {
                                                             "rates": {
                                                                 "job_type": "ENTRANCE",
                                                                 "rate": current_rate,
                                                                 "created": datetime.now(tz=pytz.UTC),
                                                                 "by": "system"
                                                             }
                                                         }})

                        rate_user = User.objects.get(pk=user_id)
                        rate_obj, created = StaffUserRate.objects.update_or_create(user=rate_user, defaults={
                            'rate': total_rate,
                            'rate_count': total_count
                        })

                        print checkers

                        if len(checkers) > 0:
                            for checker in checkers:
                                uf = UserFinanialInformation.objects.filter(user__id=checker["user_id"]).first()

                                if uf:
                                    cost_per = UserCheckerEntranceCost.objects.get(title=selected_task["ftype"])

                                    final_cost = (int(selected_task["q_count"] * cost_per.cost * cost_per.rate / 100) + 1) * 100

                                    task_detail = {
                                        "task_unique_id": selected_task["task_unique_id"],
                                        "job_unique_id": job["job_relate_uniqueid"],
                                        "total_cost": final_cost,
                                        "job_type": job["job_type"],
                                        "check_state": "DONE",
                                        "created": datetime.now(tz=pytz.UTC)

                                    }

                                    obj = {
                                        "user_id": checker["user_id"],
                                        "user_fullname": checker["fullname"],
                                        "user_username": checker["username"],
                                        "user_date_joined": checker["joined"],
                                        "user_type": "CHECK_IN",
                                        "task_detail": [],
                                        "finance_detail": {
                                            "shaba": uf.bank_shaba,
                                            "bank_name": uf.bank_name
                                        }
                                    }

                                    job_finance_record = db.job_finance.find_one({'user_id': checker["user_id"]})
                                    if job_finance_record is None:
                                        db.job_finance.insert_one(obj)

                                    db.job_finance.update_one({'user_id': checker["user_id"]},
                                                              {"$addToSet": {
                                                                  "task_detail": task_detail
                                                              }})

                                # save rate
                                obj = {
                                    "user_id": checker["user_id"],
                                    "fullname": checker["fullname"],
                                    "username": checker["username"],
                                    "total_rate": 0,
                                    "total_count": 0,
                                    "updated": datetime.now(tz=pytz.UTC),
                                    "rates": []
                                }

                                user_rate_record = db.job_users_rate.find_one({'user_id': checker["user_id"]})
                                if user_rate_record is None:
                                    db.job_users_rate.insert_one(obj)
                                    user_rate_record = obj

                                total_count = user_rate_record["total_count"] + 1
                                total_rate = ((user_rate_record["total_count"] * user_rate_record["total_rate"]) + 5) / total_count

                                db.job_users_rate.update_one({'user_id': checker["user_id"]},
                                                             {"$set": {
                                                                 "total_count": total_count,
                                                                 "total_rate": total_rate,
                                                                 "updated": datetime.now(tz=pytz.UTC)
                                                             },
                                                                 "$push": {
                                                                     "rates": {
                                                                         "job_type": "ENTRANCE",
                                                                         "rate": 5,
                                                                         "created": datetime.now(tz=pytz.UTC),
                                                                         "by": "system"
                                                                     }
                                                                 }})

                                rate_user = User.objects.get(pk=checker["user_id"])
                                rate_obj, created = StaffUserRate.objects.update_or_create(user=rate_user, defaults={
                                    'rate': total_rate,
                                    'rate_count': total_count
                                })


    except Exception, exc:
        print exc

    return redirect(request.META['HTTP_REFERER'])
    # return redirect("admin.de_jobs.entrance.detail_with_id", unique_id=unique_id, detail_id=detail_id)



@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_continue_check(request, unique_id, detail_id):
    try:
        db = connectToMongo()
        user = request.user

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id),
                               "job_owner_id": user.id})

        print job
        if job is not None and job["job_owner_id"] == user.id:
            task = None

            print "start"
            for t in job["data"]["tasks"]:
                if t["task_unique_id"] == uuid.UUID(detail_id) and t["state"] == "WAIT_FOR_REJECTED":
                    task = t
                    break

            print task
            if task:
                check_state = task["check_state"]

                if "checkers" in task:
                    print "ch1"
                    checker = task["checkers"][check_state - 1]
                    user_id = checker["user_id"]

                    uf = UserFinanialInformation.objects.filter(user__id=user_id).first()

                    if uf:
                        cost_per = UserCheckerEntranceCost.objects.get(title=task["ftype"])

                        final_cost = (int(task["q_count"] * cost_per.cost * cost_per.rate * 0.1 / 10) - 1) * 10 * -2

                        print "ch2"
                        task_detail = {
                            "task_unique_id": task["task_unique_id"],
                            "job_unique_id": job["job_relate_uniqueid"],
                            "total_cost": final_cost,
                            "job_type": job["job_type"],
                            "check_state": "W-REJECT",
                            "created": datetime.now(tz=pytz.UTC)
                        }

                        print "ch3"
                        obj = {
                            "user_id": user_id,
                            "user_fullname": checker["fullname"],
                            "user_username": checker["username"],
                            "user_date_joined": checker["joined"],
                            "user_type": "CHECK_IN",
                            "task_detail": [],
                            "finance_detail": {
                                "shaba": uf.bank_shaba,
                                "bank_name": uf.bank_name
                            }
                        }

                        job_finance_record = db.job_finance.find_one({'user_id': user_id})
                        if job_finance_record is None:
                            db.job_finance.insert_one(obj)

                        db.job_finance.update_one({'user_id': user_id},
                                                  {"$addToSet": {
                                                      "task_detail": task_detail
                                                  }})

                    # save rate
                    obj = {
                        "user_id": user_id,
                        "fullname": checker["fullname"],
                        "username": checker["username"],
                        "total_rate": 0,
                        "total_count": 0,
                        "updated": datetime.now(tz=pytz.UTC),
                        "rates": []
                    }
                    print "ch4"

                    user_rate_record = db.job_users_rate.find_one({'user_id': user_id})
                    if user_rate_record is None:
                        db.job_users_rate.insert_one(obj)
                        user_rate_record = obj

                    total_count = user_rate_record["total_count"] + 1
                    total_rate = ((user_rate_record["total_count"] * user_rate_record["total_rate"]) + 1) / total_count

                    db.job_users_rate.update_one({'user_id': user_id},
                                                 {"$set": {
                                                     "total_count": total_count,
                                                     "total_rate": total_rate,
                                                     "updated": datetime.now(tz=pytz.UTC)
                                                 },
                                                     "$addToSet": {
                                                         "rates": {
                                                             "job_type": "ENTRANCE",
                                                             "rate": 1,
                                                             "created": datetime.now(tz=pytz.UTC),
                                                             "by": "system"
                                                         }
                                                     }})

                    rated_user = User.objects.get(pk=user_id)
                    rate_obj, created = StaffUserRate.objects.update_or_create(user=rated_user, defaults={
                        'rate': total_rate,
                        'rate_count': total_count
                    })

                log = {
                    "log_type": "DEBUG",
                    "level": 1,
                    "title": "CHECK_CONTINUE",
                    "description": u"ادامه بررسی توسط مدیر پنل %s - %s داده شد." % (job["job_owner"]["fullname"], job["job_owner"]["username"]),
                    "created": datetime.now(tz=pytz.UTC)
                }

                check = "WAIT_FOR_CHECK"
                if check_state == 2:
                    check = "CHECK_DONE"

                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                   'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                   'job_owner_id': user.id},
                                  {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                            "updated": datetime.now(tz=pytz.UTC),
                                            "status": "STARTED",
                                            "data.tasks.$.state": check
                                            },
                                   "$addToSet": {
                                       "data.tasks.$.logs": log
                                   }})

    except Exception, exc:
        print exc

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_start_check(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        user = request.user
        holding = {
            "user_id": user.id,
            "username": user.username,
            "fullname": user.get_full_name(),
            "joined": user.date_joined
        }

        log = {
            "log_type": "INFO",
            "level": 1,
            "title": "CHECK_STARTED",
            "description": u"بررسی مرحله اول توسط %s - %s شروع شده است." % (user.get_full_name(), user.username),
            "created": datetime.now(tz=pytz.UTC)
        }

        db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id),
                           'data.tasks.state': "WAIT_FOR_CHECK"},
                          {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                    "updated": datetime.now(tz=pytz.UTC),
                                    "data.tasks.$.holding_editor": holding,
                                    "status": "STARTED",
                                    "data.tasks.$.state": "CHECK_STARTED",
                                    "data.tasks.$.checkers.0": holding,
                                    "data.tasks.$.check_state": 1
                                    },
                           "$addToSet": {
                               "data.tasks.$.logs": log
                           }})

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_start_check_wrong_file(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id)})
        if job is not None:
            checker = None
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    if "checkers" in task and len(task["checkers"]) > 0:
                        checker = task["checkers"][0]

            if checker is not None:
                checker["description"] = "wrong_file"

                user = User.objects.get(pk=checker["user_id"])
                log = {
                    "log_type": "INFO",
                    "level": 1,
                    "title": "CHECK_STARTED",
                    "description": u"فایل توسط بررسی کننده اول %s - %s اشتباه بارگذاری شده است" % (user.get_full_name(), user.username),
                    "created": datetime.now(tz=pytz.UTC)
                }

                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                   'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                   'data.tasks.state': "WAIT_FOR_REJECTED"},
                                  {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                            "updated": datetime.now(tz=pytz.UTC),
                                            "data.tasks.$.holding_editor": checker,
                                            "status": "STARTED",
                                            "data.tasks.$.state": "CHECK_STARTED",
                                            },
                                   "$addToSet": {
                                       "data.tasks.$.logs": log
                                   }})

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_start_check2(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        user = request.user
        holding = {
            "user_id": user.id,
            "username": user.username,
            "fullname": user.get_full_name(),
            "joined": user.date_joined
        }

        log = {
            "log_type": "INFO",
            "level": 1,
            "title": "CHECK2_STARTED",
            "description": u"بررسی مرحله دوم توسط %s - %s شروع شده است." % (user.get_full_name(), user.username),
            "created": datetime.now(tz=pytz.UTC)
        }

        g = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                             'data.tasks.task_unique_id': uuid.UUID(detail_id),
                             'data.tasks.state': "CHECK_DONE"})

        for task in g["data"]["tasks"]:
            if task["state"] == "CHECK_DONE" and task["holding_editor"]["user_id"] != user.id and task[
                "task_unique_id"] == uuid.UUID(detail_id):
                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                   'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                   'data.tasks.state': "CHECK_DONE"
                                   },
                                  {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                            "updated": datetime.now(tz=pytz.UTC),
                                            "data.tasks.$.holding_editor": holding,
                                            "status": "STARTED",
                                            "data.tasks.$.state": "CHECK2_STARTED",
                                            "data.tasks.$.checkers.1": holding,
                                            "data.tasks.$.check_state": 2

                },
                                   "$addToSet": {
                                       "data.tasks.$.logs": log
                                   }})
                break

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_detail_start_check2_wrong_file(request, unique_id, detail_id):
    try:
        db = connectToMongo()

        job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                           'data.tasks.task_unique_id': uuid.UUID(detail_id)})
        if job is not None:
            checker = None
            for task in job["data"]["tasks"]:
                if task["task_unique_id"] == uuid.UUID(detail_id):
                    if "checkers" in task and len(task["checkers"]) > 1:
                        checker = task["checkers"][1]

            if checker is not None:
                checker["description"] = "wrong_file"

                user = User.objects.get(pk=checker["user_id"])
                log = {
                    "log_type": "INFO",
                    "level": 1,
                    "title": "CHECK2_STARTED",
                    "description": u"فایل توسط بررسی کننده دوم %s - %s اشتباه بارگذاری شده است" % (user.get_full_name(), user.username),
                    "created": datetime.now(tz=pytz.UTC)
                }

                db.job.update_one({'job_relate_uniqueid': uuid.UUID(unique_id),
                                   'data.tasks.task_unique_id': uuid.UUID(detail_id),
                                   'data.tasks.state': "WAIT_FOR_REJECTED"},
                                  {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                            "updated": datetime.now(tz=pytz.UTC),
                                            "data.tasks.$.holding_editor": checker,
                                            "status": "STARTED",
                                            "data.tasks.$.state": "CHECK2_STARTED",
                                            },
                                   "$addToSet": {
                                       "data.tasks.$.logs": log
                                   }})

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_check_done(request):
    try:
        db = connectToMongo()
        user = request.user

        if request.method == "POST":
            form = JobTaskCheckDoneForm(request.POST or None, files=request.FILES)

            if form.is_valid():
                job_unique_key = form.cleaned_data["job_unique_key"]
                task_unique_key = form.cleaned_data["task_unique_key"]
                term_file = form.cleaned_data['term_file']
                misspelling_count = form.cleaned_data['misspelling_count']
                description = form.cleaned_data['description']

                log = {
                    "log_type": "WARNING",
                    "level": 1,
                    "title": "CHECK_DONE",
                    "description": u"بررسی مرحله اول توسط %s _ %s به اتمام رسید. (با %s خطای تایپی) ... توضیحات: %s" % (
                        user.get_full_name(), user.username, misspelling_count, description),
                    "created": datetime.now(tz=pytz.UTC)
                }

                job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key)})
                if job is not None:

                    selected_task = None
                    for task in job["data"]["tasks"]:
                        if task["task_unique_id"] == uuid.UUID(task_unique_key):
                            selected_task = task

                    fs = GridFS(db)

                    if "term_file" in selected_task and selected_task["term_file"] is not None:
                        if fs.exists(selected_task["term_file"]):
                            fs.delete(selected_task["term_file"])

                    fs_obj = fs.put(term_file,
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

                    db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key),
                                       'data.tasks.holding_editor.user_id': request.user.id,
                                       'data.tasks.state': "CHECK_STARTED"},
                                      {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                "updated": datetime.now(tz=pytz.UTC),
                                                "status": "STARTED",
                                                "data.tasks.$.state": "CHECK_DONE",
                                                "data.tasks.$.term_file": fs_obj,
                                                'data.tasks.$.check_done_1_misspelling': misspelling_count
                                                },
                                       "$addToSet": {
                                           "data.tasks.$.logs": log
                                       }})

                    title = ""
                    ftype = ""
                    for t in job["data"]["tasks"]:
                        if t["task_unique_id"] == uuid.UUID(task_unique_key):
                            title = t["lesson_title"]
                            ftype = t["ftype"]

                    task = copy.deepcopy(job["data"])
                    del task["tasks"]
                    task["lesson_title"] = title
                    task["ftype"] = ftype

                    check_obj = {
                        "checker_user_id": user.id,
                        "checker_username": user.username,
                        "checker_fullname": user.get_full_name(),
                        "created": datetime.now(tz=pytz.UTC),
                        "check_type": "ENTRANCE",
                        "check_status": "DONE-1",
                        "check_data": task
                    }

                    db.job_checks.insert_one(check_obj)

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_task_accepted(request):
    try:
        db = connectToMongo()
        user = request.user

        if request.method == "POST":
            form = JobTaskCheckDoneForm(request.POST or None, files=request.FILES)

            if form.is_valid():
                job_unique_key = form.cleaned_data["job_unique_key"]
                task_unique_key = form.cleaned_data["task_unique_key"]
                term_file = form.cleaned_data['term_file']
                misspelling_count = form.cleaned_data['misspelling_count']
                description = form.cleaned_data['description']

                log = {
                    "log_type": "WARNING",
                    "level": 1,
                    "title": "ACCEPTED",
                    "description": u"بررسی نهایی توسط %s - %s به اتمام رسید (با %s خطای تایپی) و مورد قبول واقع شد. ... توضیحات: %s" % (
                        user.get_full_name(), user.username, misspelling_count, description),
                    "created": datetime.now(tz=pytz.UTC)
                }

                job = db.job.find_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key)})

                if job is not None:
                    title = ""
                    ftype = ""
                    selected_task = None
                    for t in job["data"]["tasks"]:
                        if t["task_unique_id"] == uuid.UUID(task_unique_key):
                            selected_task = t
                            title = t["lesson_title"]
                            ftype = t["ftype"]


                    fs = GridFS(db)

                    if "term_file" in selected_task and selected_task["term_file"] is not None:
                        if fs.exists(selected_task["term_file"]):
                            fs.delete(selected_task["term_file"])

                    fs_obj = fs.put(term_file,
                                    content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

                    db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                       'data.tasks.task_unique_id': uuid.UUID(task_unique_key),
                                       'data.tasks.holding_editor.user_id': request.user.id,
                                       'data.tasks.state': "CHECK2_STARTED"},
                                      {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                "updated": datetime.now(tz=pytz.UTC),
                                                "status": "STARTED",
                                                "data.tasks.$.state": "ACCEPTED",
                                                "data.tasks.$.term_file": fs_obj,
                                                'data.tasks.$.check_done_1_misspelling': misspelling_count
                                                },
                                       "$addToSet": {
                                           "data.tasks.$.logs": log
                                       }})



                    task = copy.deepcopy(job["data"])
                    del task["tasks"]
                    task["lesson_title"] = title
                    task["ftype"] = ftype

                    check_obj = {
                        "checker_user_id": user.id,
                        "checker_username": user.username,
                        "checker_fullname": user.get_full_name(),
                        "created": datetime.now(tz=pytz.UTC),
                        "check_type": "ENTRANCE",
                        "check_status": "DONE-2",
                        "check_data": task
                    }

                    db.job_checks.insert_one(check_obj)

    except Exception, exc:
        print exc

    return redirect('admin.de_jobs.entrance.list')


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_detail_task_rejected(request):
    try:
        db = connectToMongo()
        user = request.user

        if request.method == "POST":
            form = JobTaskEntranceRejectForm(request.POST or None)

            if form.is_valid():
                job_unique_key = form.cleaned_data["job_unique_key"]
                task_unique_key = form.cleaned_data["task_unique_key"]
                description = form.cleaned_data['description']
                reject_reason = form.cleaned_data['reject_reason']

                reject_str = ""
                for item in reject_reason:
                    for item2 in RejectReasonChoices:
                        if item2[0] == item:
                            reject_str += "- %s " % item2[1]

                log = {
                    "log_type": "DANGER",
                    "level": 1,
                    "title": "WAIT_FOR_REJECTED",
                    "description": u"بررسی توسط %s - %s مردود گردید. دلایل: %s" % (user.get_full_name(), user.username, reject_str),
                    "created": datetime.now(tz=pytz.UTC)
                }

                g = db.job.find_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                     'data.tasks.task_unique_id': uuid.UUID(task_unique_key)})

                for task in g["data"]["tasks"]:
                    if task["task_unique_id"] == uuid.UUID(task_unique_key) and task["state"] in ["CHECK_STARTED",
                                                                                                  "CHECK2_STARTED"] and \
                                    task["holding_editor"]["user_id"] == user.id:
                        db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                           'data.tasks.task_unique_id': uuid.UUID(task_unique_key)},
                                          {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                    "updated": datetime.now(tz=pytz.UTC),
                                                    "status": "STARTED",
                                                    "data.tasks.$.state": "WAIT_FOR_REJECTED",
                                                    "data.tasks.$.reject_reason": reject_reason,
                                                    "data.tasks.$.reject_description": description
                                                    },
                                           "$addToSet": {
                                               "data.tasks.$.logs": log
                                           }})

                    elif task["task_unique_id"] == uuid.UUID(task_unique_key) and task["state"] == "TYPE_DONE" and g["job_owner_id"] == user.id:
                        holding_editor = {
                            "user_id": user.id,
                            "username": user.username,
                            "fullname": user.get_full_name(),
                            "joined": user.date_joined
                        }
                        db.job.update_one({'job_relate_uniqueid': uuid.UUID(job_unique_key),
                                           'data.tasks.task_unique_id': uuid.UUID(task_unique_key)},
                                          {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                    "updated": datetime.now(tz=pytz.UTC),
                                                    "data.tasks.$.holding_editor": holding_editor,
                                                    "status": "STARTED",
                                                    "data.tasks.$.state": "WAIT_FOR_REJECTED",
                                                    "data.tasks.$.reject_reason": reject_reason,
                                                    "data.tasks.$.reject_description": description
                                                    },
                                           "$addToSet": {
                                               "data.tasks.$.logs": log
                                           }})

                title = ""
                ftype = ""
                for t in g["data"]["tasks"]:
                    if t["task_unique_id"] == uuid.UUID(task_unique_key):
                        title = t["lesson_title"]
                        ftype = t["ftype"]

                task = copy.deepcopy(g["data"])
                del task["tasks"]
                task["lesson_title"] = title
                task["ftype"] = ftype

                check_obj = {
                    "checker_user_id": user.id,
                    "checker_username": user.username,
                    "checker_fullname": user.get_full_name(),
                    "created": datetime.now(tz=pytz.UTC),
                    "check_type": "ENTRANCE",
                    "check_status": "REJECT",
                    "check_reject_reason": reject_reason,
                    "check_data": task
                }

                db.job_checks.insert_one(check_obj)

    except Exception, exc:
        print exc

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_tasks_news_list(request):
    menu_selected = "jobs"
    inner_menu_selected = "entrance_jobs_list"

    user_group_name = None
    jobs = None
    form = JobTaskAddTypistForm()
    form2 = JobTaskFinalPriceForm()
    form3 = JobTaskEntranceRejectForm()

    page = int(request.GET.get('page', 1))
    per_page = 10

    # get user group name
    user_group_names = request.user.groups.all()
    jobs_list = None

    db = connectToMongo()
    if 'master_operator' in [grp.name for grp in user_group_names] or 'administrator' in [grp.name for grp in
                                                                                          user_group_names]:
        jobs_list = db.job.find({'$and': [{'status': {'$ne': "FINISHED"}}, {'job_type': "ENTRANCE"}]}).sort(
            [('updated', -1)]).skip((page - 1) * per_page).limit(per_page)

        user_group_name = "master_operator"

    elif 'job_supervisor' in [grp.name for grp in user_group_names]:

        jobs_list = db.job.find({'$and': [{'status': {'$ne': "FINISHED"}}, {'job_type': "ENTRANCE"}, {'job_owner_id': request.user.id}]}).sort(
            [('updated', -1)]).skip((page - 1) * per_page).limit(per_page)

        user_group_name = "master_operator"

    d = dict(menul=menu_settings.menus, msel=menu_selected, jobs=jobs_list, ugn=user_group_name, page=page + 1,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus, form=form, form2=form2,
             form3=form3)
    return render_to_response("admin/de_jobs/entrance_job_news.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.entrance.manage', raise_exception=True)
def entrance_job_tasks_typist_state(request):
    menu_selected = "jobs"
    inner_menu_selected = "entrance_jobs_list"

    db = connectToMongo()
    jobs_list = db.job.find({'$and': [{'status': {'$ne': "FINISHED"}}, {'job_type': "ENTRANCE"}]})

    users = {}
    for job in jobs_list:
        if job["status"] == "STARTED":

            for task in job["data"]["tasks"]:
                if task["state"] != "CREATED":
                    user_username = task["main_editor"]["username"]

                    if not users.has_key(user_username):
                        print type(task["main_editor"]["joined"])

                        users[user_username] = {
                            "user_id": task["main_editor"]["user_id"],
                            "fullname": task["main_editor"]["fullname"],
                            "joined": task["main_editor"]["joined"],
                            "not_started": 0,
                            "type_started": 0,
                            "type_done": 0,
                            "type_in_check": 0,
                            "type_rejected": 0
                        }
                    if task["state"] == "WAIT_FOR_TYPE":
                        users[user_username]["not_started"] += 1
                    elif task["state"] == "TYPE_STARTED":
                        users[user_username]["type_started"] += 1
                    elif task["state"] == "TYPE_DONE":
                        users[user_username]["type_done"] += 1
                    elif task["state"] == "WAIT_FOR_CHECK" or task["state"] == "CHECK_STARTED" or task[
                        "state"] == "CHECK_DONE" or task["state"] == "CHECK2_STARTED" or task["state"] == "ACCEPTED" \
                            or task["state"] == "WAIT_FOR_REJECTED":
                        users[user_username]["type_in_check"] += 1
                    elif task["state"] == "REJECTED":
                        users[user_username]["type_rejected"] += 1

    d = dict(menul=menu_settings.menus, msel=menu_selected, result=users,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus)
    return render_to_response("admin/de_jobs/entrance_job_editor_details.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.finance', raise_exception=True)
def entrance_job_finance(request):
    menu_selected = "jobs"
    inner_menu_selected = "jobs_finance"

    form = JobTaskEntrancePayOffForm()

    db = connectToMongo()
    finance_list = db.job_finance.find({'task_detail.job_type': "ENTRANCE"})

    d = dict(menul=menu_settings.menus, msel=menu_selected, result=finance_list, form=form,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus)
    return render_to_response("admin/de_jobs/entrance_job_finance.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.finance', raise_exception=True)
def entrance_job_finance_accounting(request, unique_id, detail_id, user_id):
    db = connectToMongo()
    db.job_finance.update_one({'task_detail.job_unique_id': uuid.UUID(unique_id),
                               'task_detail.task_unique_id': uuid.UUID(detail_id),
                               'user_id': int(user_id)
                               },
                              {'$set': {"task_detail.$.status": "ACCOUNTING"}
                               })

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.finance', raise_exception=True)
def entrance_job_finance_accounting_all(request, user_id):
    db = connectToMongo()
    db.job_finance.update({
                               'user_id': int(user_id)
                               },
                              {'$set': {"task_detail.$[].status": "ACCOUNTING"}
                               }, multi=True)

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.finance', raise_exception=True)
def entrance_job_finance_accounting_list(request):
    db = connectToMongo()
    finance_list = db.job_finance.find({'task_detail.job_type': "ENTRANCE"})

    bank_name = "PASARGAD"
    content = ""

    for f in finance_list:
        u = User.objects.get(pk=f["user_id"])
        total_cost = 0
        for task in f["task_detail"]:
            if "status" in task and task["status"] == "ACCOUNTING":
                total_cost += task["total_cost"]

        if total_cost > 0:
            if bank_name == "PASARGAD":
                deposite_id = "cdid%s" % str(int(time.time()))
                content += "%s,%s,%s,%s,%s,%s\r\n" % (f["finance_detail"]["shaba"],
                                                      str(total_cost * 10),
                                                      u.first_name,
                                                      u.last_name,
                                                      u"پرداخت بابت تایپ",
                                                      deposite_id
                                                      )

                db.job_finance.update_one({'user_id': u.id,
                                           'task_detail.status': "ACCOUNTING"},
                                          {
                                              '$set': {
                                                  'task_detail.$.deposit_id': deposite_id
                                              }
                                          })

    d = datetime.now()
    response = HttpResponse(content=content.encode('utf-8'))
    response['Content-Disposition'] = 'attachment; filename="accounting-%s-%s-%s.txt"' \
                                      % (d.year, d.month, d.day)

    return response


@login_required
@group_permission_required('main.de_jobs.finance', raise_exception=True)
def entrance_job_finance_pay_off(request):
    try:
        total_cost = 0

        form = JobTaskEntrancePayOffForm(request.POST or None)
        if form.is_valid():
            user_id = form.cleaned_data["user_id"]
            deposit_id = form.cleaned_data["deposit_id"]
            issue_tracking = form.cleaned_data["issue_tracking"]

            user = User.objects.get(pk=user_id)

            db = connectToMongo()
            finance_list = db.job_finance.find_one({'user_id': int(user_id)})

            for task in finance_list["task_detail"]:
                if "status" in task and task["status"] == "ACCOUNTING" and task["job_type"] == "ENTRANCE":

                    p = EntranceEditorFinanialPayment()
                    p.user = user
                    p.payed = int(task["total_cost"])
                    p.deposit_id = deposit_id
                    p.job_type = "ENTRANCE"
                    p.job_id = task["job_unique_id"]
                    p.description = u"پرداخت بابت تایپ فایل %s" % task["task_unique_id"].hex
                    p.issue_tracking = issue_tracking

                    p.save()
                    log = {
                        "log_type": "INFO",
                        "level": 1,
                        "title": "PAYED",
                        "description": u"پول به تایپیست پرداخت شد با شماره پیگیری بانک %s" % issue_tracking,
                        "created": datetime.now(tz=pytz.UTC)
                    }

                    db.job.update_one({'job_relate_uniqueid': task["job_unique_id"],
                                       'data.tasks.task_unique_id': task["task_unique_id"]},
                                      {'$set': {"data.tasks.$.updated": datetime.now(tz=pytz.UTC),
                                                "updated": datetime.now(tz=pytz.UTC),
                                                "data.tasks.$.state": "PAYED"
                                                },
                                       "$addToSet": {
                                           "data.tasks.$.logs": log
                                       }})

                    total_cost += int(task["total_cost"])

                    db.job_finance.update({'user_id': int(user_id)}, {
                        '$pull': {
                            'task_detail': {'task_unique_id': task["task_unique_id"]}
                        }
                    })

            if settings.DEV_ENVIRONMENT == "deploy":
                if total_cost > 0:
                    text1 = user.username
                    text2 = total_cost

                    provider = "kavenegar"
                    if provider == "kavenegar":
                        response = sendSMS2(provider, user.username, text1, text2, "editor_payment")

    except Exception, exc:
        print exc
        pass

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.finance', raise_exception=True)
def entrance_job_checker_finance_pay_off(request):
    try:
        form = JobTaskEntrancePayOffForm(request.POST or None)
        if form.is_valid():
            user_id = form.cleaned_data["user_id"]
            deposit_id = form.cleaned_data["deposit_id"]
            issue_tracking = form.cleaned_data["issue_tracking"]

            user = User.objects.get(pk=user_id)

            db = connectToMongo()
            finance_list = db.job_finance.find_one({'user_id': int(user_id)})

            total_cost = 0
            payed_for_done = 0
            payed_for_reject = 0
            payed_wrong_reject = 0
            detail_description = u""
            for task in finance_list["task_detail"]:
                if "status" in task and task["status"] == "ACCOUNTING" and task["job_type"] == "ENTRANCE":
                    total_cost += int(task["total_cost"])
                    detail_description += u"(%s: %d)" % (task["task_unique_id"].hex, total_cost)

                    if task["check_state"] == "DONE":
                        payed_for_done += 1
                    elif task["check_state"] == "REJECT":
                        payed_for_reject += 1
                    elif task["check_state"] == "W-REJECT":
                        payed_wrong_reject += 1

            desc = u"پرداخت بابت بررسی فایل - تایید شده: %d - رد شده: %d و اشتباه رد شده: %d" % (payed_for_done, payed_for_reject, payed_wrong_reject) + u"(%s)" % detail_description
            p = EntranceCheckerFinanialPayment()
            p.user = user
            p.payed = total_cost
            p.deposit_id = deposit_id
            p.job_type = "ENTRANCE"
            p.description = force_text(desc)
            p.issue_tracking = issue_tracking

            p.save()

            for task in finance_list["task_detail"]:
                if "status" in task and task["status"] == "ACCOUNTING" and task["job_type"] == "ENTRANCE":
                    db.job_finance.update({'user_id': int(user_id)}, {
                        '$pull': {
                            'task_detail': {'task_unique_id': task["task_unique_id"]}
                        }
                    })

            if settings.DEV_ENVIRONMENT == "deploy":
                if total_cost > 0:
                    text1 = user.username
                    text2 = total_cost

                    provider = "kavenegar"
                    if provider == "kavenegar":
                        response = sendSMS2(provider, user.username, text1, text2, "editor_payment")

    except Exception, exc:
        print exc
        pass

    return redirect(request.META['HTTP_REFERER'])


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_editor_finance(request):
    menu_selected = "jobs"
    inner_menu_selected = "entrance_jobs_list"

    page = request.GET.get('page', 1)
    payments = []
    not_seen = []

    user_group_names = request.user.groups.all()
    if 'editor' in [grp.name for grp in user_group_names]:
        db = connectToMongo()

        seen = EntranceEditorFinanialPayment.objects.filter(seen=False, user=request.user)
        for rec in seen:
            not_seen.append(rec.id)

        payments_list = EntranceEditorFinanialPayment.objects.filter(user=request.user).order_by('-created', 'seen')
        paginator = Paginator(payments_list, 20)
        try:
            payments = paginator.page(page)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)

        EntranceEditorFinanialPayment.objects.filter(seen=False).update(seen=True)

    d = dict(menul=menu_settings.menus, msel=menu_selected, payments=payments, not_seen=not_seen,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus, seen_count=len(not_seen))
    return render_to_response("admin/de_jobs/entrance_job_editor_payment.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.entrance', raise_exception=True)
def entrance_job_checker_finance(request):
    menu_selected = "jobs"
    inner_menu_selected = "entrance_jobs_list"

    page = request.GET.get('page', 1)
    payments = []
    not_seen = []

    payed_for_done = 0
    payed_for_reject = 0
    payed_wrong_reject = 0

    payed_for_done_cost = 0
    payed_for_reject_cost = 0
    payed_wrong_reject_cost = 0

    user_group_names = request.user.groups.all()
    if 'check_in' in [grp.name for grp in user_group_names]:
        db = connectToMongo()
        finance_list = db.job_finance.find_one({'user_id': request.user.id})

        if finance_list:
            for task in finance_list["task_detail"]:
                if task["job_type"] == "ENTRANCE":
                    if task["check_state"] == "DONE":
                        payed_for_done += 1
                        payed_for_done_cost += int(task["total_cost"])
                    elif task["check_state"] == "REJECT":
                        payed_for_reject += 1
                        payed_for_reject_cost += int(task["total_cost"])
                    elif task["check_state"] == "W-REJECT":
                        payed_wrong_reject += 1
                        payed_wrong_reject_cost += int(task["total_cost"])

        seen = EntranceCheckerFinanialPayment.objects.filter(seen=False, user=request.user)
        for rec in seen:
            not_seen.append(rec.id)

        payments_list = EntranceCheckerFinanialPayment.objects.filter(user=request.user).order_by('-created', 'seen')
        paginator = Paginator(payments_list, 20)
        try:
            payments = paginator.page(page)
        except PageNotAnInteger:
            payments = paginator.page(1)
        except EmptyPage:
            payments = paginator.page(paginator.num_pages)

        EntranceCheckerFinanialPayment.objects.filter(seen=False).update(seen=True)

    d = dict(menul=menu_settings.menus, msel=menu_selected, payments=payments, not_seen=not_seen,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus, seen_count=len(not_seen),
             payed_for_done=payed_for_done, payed_for_reject=payed_for_reject, payed_wrong_reject=payed_wrong_reject,
             payed_for_done_cost=payed_for_done_cost, payed_for_reject_cost=payed_for_reject_cost, payed_wrong_reject_cost=payed_wrong_reject_cost)
    return render_to_response("admin/de_jobs/entrance_job_checker_payment.html", d,
                              context_instance=RequestContext(request))


@login_required
@group_permission_required('main.de_jobs.settings', raise_exception=True)
def entrance_job_settings_checkers_cost(request):
    menu_selected = "jobs"
    inner_menu_selected = "jobs_settings"

    form = None

    if request.method == "GET":
        form = UserCheckerEntranceCostAddForm()
    if request.method == "POST":
        form = UserCheckerEntranceCostAddForm(request.POST or None)

        try:
            if form.is_valid():

                title = form.cleaned_data["title"]
                cost = form.cleaned_data["cost"]
                rate = form.cleaned_data["rate"]

                obj, created = UserCheckerEntranceCost.objects.update_or_create(title=title, defaults={'cost': cost, 'rate': rate})


                return redirect("admin.de_jobs.settings.checker_cost")

        except Exception, exc:
            print exc


    costs = UserCheckerEntranceCost.objects.all()

    d = dict(menul=menu_settings.menus, msel=menu_selected, costs=costs, form=form,
             minnersel=inner_menu_selected, menuinner=jobs_menu_settings.jobs_menus)
    return render_to_response("admin/de_jobs/entrance_job_settings_checker_cost.html", d,
                          context_instance=RequestContext(request))
