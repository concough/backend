import datetime
import uuid

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from main.models import ConcoughActivity, ConcoughProductStatistic

__author__ = 'abolfazl'


def create_concough_activity(activity_type, target):
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)

    similar_activities = ConcoughActivity.objects.filter(activity_type=activity_type,
                                                    created__gte=last_minute)

    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_activities = similar_activities.filter(target_ct=target_ct,
                                                       target_id=target.id)

    if not similar_activities:
        # no existing actions found
        action = ConcoughActivity(target=target, activity_type=activity_type)
        action.save()
        return True

    return False


def create_product_statistic(target):
    if target:
        try:
            product = ConcoughProductStatistic()
            product.target = target
            product.save()
        except Exception, exc:
            print exc


def get_help_filename(filename):
    return "helps/help_%s.%s" % (uuid.uuid4().hex, filename.split('.')[-1])