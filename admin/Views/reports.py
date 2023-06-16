# coding=utf-8
from __future__ import division

import json

import pytz
import uuid
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext

from admin.Forms.DEReportsForm import ReportExternalCampaignAddForm
from admin.Helpers import menu_settings
from admin.Helpers.reports_menu_settings import reports_menus
from api.models import Profile, UserRegisteredDevice, PreAuth
from main.Helpers.decorators import group_permission_required
from main.models import ConcoughUserPurchased, ConcoughProductStatistic, ConcoughActivity, SmsCallStatus
from main.models_functions import connectToMongo


@login_required
@group_permission_required('main.reports', raise_exception=True)
def reports_general(request):
    menu_selected = "reports"
    inner_menu_selected = "reports_general"

    users_count = User.objects.count()
    profile_male_count = Profile.objects.filter(gender="M").count()
    profile_female_count = Profile.objects.filter(gender="F").count()
    profile_other_count = Profile.objects.filter(gender="O").count()
    devices_count = UserRegisteredDevice.objects.count()

    staff_users = User.objects.filter(is_staff=True).count()

    purchased_count = ConcoughUserPurchased.objects.count()
    purchased_count_downloaded = ConcoughUserPurchased.objects.filter(downloaded__gte=1).count()

    all_downloaded = ConcoughProductStatistic.objects.aggregate(Sum('downloaded'))
    all_downloaded = all_downloaded["downloaded__sum"]

    distinct_purchased_user_count = ConcoughUserPurchased.objects.values("user").distinct().count()

    purchased_per_user = purchased_count / (profile_male_count + profile_female_count + profile_other_count)
    downloaded_per_purchased = all_downloaded / purchased_count

    activity_count = ConcoughActivity.objects.count()

    sms_count = SmsCallStatus.objects.count()
    sms_count_signup = SmsCallStatus.objects.filter(send_type="SIGNUP").count()

    preauth_signup_count = PreAuth.objects.filter(auth_type="SIGNUP").count()
    preauth_forgot_count = PreAuth.objects.filter(auth_type="PASS_RECOVERY").count()

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected, menuinner=reports_menus,
             users_count=users_count, profile_female_count=profile_female_count, profile_male_count=profile_male_count,
             profile_other_count=profile_other_count, purchased_count=purchased_count, devices_count=devices_count,
             staff_users_count=staff_users, purchased_count_downloaded=purchased_count_downloaded,
             all_downloaded_count=all_downloaded,
             distinct_purchased_user_count=distinct_purchased_user_count, purchased_per_user=purchased_per_user,
             downloaded_per_purchased=downloaded_per_purchased, activity_count=activity_count,
             sms_count=sms_count, sms_count_signup=sms_count_signup, preauth_forgot_count=preauth_forgot_count,
             preauth_signup_count=preauth_signup_count)
    return render_to_response("admin/reports/reports_general.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.reports.campaign', raise_exception=True)
def reports_campaign(request):
    menu_selected = "reports"
    inner_menu_selected = "reports_campaign"

    db = connectToMongo()
    campaigns = []
    hide_campaigns = []
    form = ReportExternalCampaignAddForm()

    try:
        campaigns_name = db.external_campaign_names.find()
        if campaigns_name.count() > 0:
            for camp in campaigns_name:
                campaign_count = db.external_campaign.find({'from_who': camp["title"]}).count()
                campaign_list = db.external_campaign.find({'from_who': camp["title"]}).sort([('created', -1)])

                campaign_item = None
                if campaign_list.count() > 0:
                    campaign_item = campaign_list[0]

                if campaign_item:
                    obj = {
                        "unique_id": camp["unique_id"],
                        "title": camp["title"],
                        "created": camp["created"],
                        "count": campaign_count,
                        "last_redirect": campaign_item["redirected_to"],
                        "last_updated": campaign_item["created"]
                    }
                else:
                    obj = {
                        "unique_id": camp["unique_id"],
                        "title": camp["title"],
                        "created": camp["created"],
                        "count": campaign_count,
                        "last_redirect": "",
                        "last_updated": datetime.now(tz=pytz.UTC)
                    }

                if camp["hide"] == False:
                    campaigns.append(obj)
                else:
                    hide_campaigns.append(obj)
    except:
        pass

    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected, menuinner=reports_menus,
             campaigns=campaigns, hide_campaigns=hide_campaigns, form=form)
    return render_to_response("admin/reports/reports_campaign.html", d, context_instance=RequestContext(request))


@login_required
@group_permission_required('main.reports.campaign', raise_exception=True)
def reports_campaign_add(request):
    if request.method == "POST":
        form = ReportExternalCampaignAddForm(request.POST or None)
        if form.is_valid():
            title = form.cleaned_data["title"]

            db = connectToMongo()
            campain_obj = db.external_campaign_names.find_one({'title': title})
            if campain_obj == None:
                obj = {
                    'title': title,
                    'created': datetime.now(tz=pytz.UTC),
                    'unique_id': uuid.uuid4(),
                    'hide': False
                }

                db.external_campaign_names.insert(obj)
            else:
                db.external_campaign_names.update_one({'title': title}, {
                    "$set": {
                        "hide": False
                    }
                })
                pass

    return redirect("admin.reports.campaign")


@login_required
@group_permission_required('main.reports.campaign', raise_exception=True)
def reports_campaign_del(request, unique_id):
    try:
        db = connectToMongo()
        campain_obj = db.external_campaign_names.find_one({'unique_id': uuid.UUID(unique_id)})
        if campain_obj != None:
            db.external_campaign_names.update_one({'unique_id': uuid.UUID(unique_id)}, {
                "$set": {
                    "hide": True
                }
            })
            pass
    except:
        pass

    return redirect("admin.reports.campaign")


@login_required
@group_permission_required('main.reports.campaign', raise_exception=True)
def reports_campaign_show(request, unique_id):
    try:
        db = connectToMongo()
        campain_obj = db.external_campaign_names.find_one({'unique_id': uuid.UUID(unique_id)})
        if campain_obj != None:
            db.external_campaign_names.update_one({'unique_id': uuid.UUID(unique_id)}, {
                "$set": {
                    "hide": False
                }
            })
            pass
    except:
        pass

    return redirect("admin.reports.campaign")


@login_required
@group_permission_required('main.reports.campaign', raise_exception=True)
def reports_campaign_sync(request):
    try:
        db = connectToMongo()
        items = db.external_campaign.distinct("from_who")

        for item in items:
            campain_obj = db.external_campaign_names.find_one({'title': item})
            if campain_obj == None:
                obj = {
                    'title': item,
                    'created': datetime.now(tz=pytz.UTC),
                    'unique_id': uuid.uuid4(),
                    'hide': False
                }

                db.external_campaign_names.insert(obj)
            else:
                pass

    except:
        pass

    return redirect("admin.reports.campaign")


@login_required
@group_permission_required('main.reports.campaign', raise_exception=True)
def reports_campaign_chart(request, unique_id):
    menu_selected = "reports"
    inner_menu_selected = "reports_campaign"

    camp = None
    try:
        db = connectToMongo()
        campaign = db.external_campaign_names.find_one({'unique_id': uuid.UUID(unique_id)})
        if campaign is not None:

            now = datetime.now(tz=pytz.UTC)
            now_30days = now - timedelta(days=30)
            criteria = now_30days

            display_array = []
            while now_30days <= now:
                key = "%04d-%02d-%02d" % (now_30days.year, now_30days.month, now_30days.day)
                display_array.append({
                    'x': key,
                    'y': 0
                })

                now_30days = now_30days + timedelta(days=1)

            print criteria

            items = db.external_campaign.aggregate([
                {'$match': {'from_who': campaign["title"], 'created': { "$gt":  criteria}} },
                {
                    "$project": {
                        "y": {
                            "$year": "$created"
                        },
                        "m": {
                            "$month": "$created"
                        },
                        "d": {
                            "$dayOfMonth": "$created"
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": "$y",
                            "month": "$m",
                            "day": "$d"
                        },
                        'count': {
                            "$sum": 1
                        }
                    }
                },
                {
                    '$sort': {
                        "_id.year": -1,
                        "_id.month": -1,
                        "_id.day": -1
                    }
                }])

            for item in items:
                key = "%04d-%02d-%02d" % (item["_id"]["year"], item["_id"]["month"], item["_id"]["day"])
                for d in display_array:
                    if d["x"] == key:
                        d["y"] = item["count"]
                        break

            campaign_title = u"کمپین %s" % campaign["title"]
            obj = {
                "labels": [],
                "datasets": [{
                    "label": campaign_title,
                    "backgroundColor": "#d9534f",
                    "data": []
                }]
            }
            for item in display_array:
                obj["labels"].append(item["x"])
                obj["datasets"][0]["data"].append(item["y"])

    except Exception, exc:
        print exc
        pass
    d = dict(menul=menu_settings.menus, msel=menu_selected, minnersel=inner_menu_selected, menuinner=reports_menus,
             camp=campaign, display_array=json.dumps(obj) )
    return render_to_response("admin/reports/reports_campaign_chart.html", d, context_instance=RequestContext(request))
