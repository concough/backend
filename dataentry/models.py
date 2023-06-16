import os
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils.datetime_safe import datetime
from main.models import Entrance, EntranceBookletDetail


# This is for creating migrations
class Task(models.Model):
    user = models.ForeignKey(User, related_name="assigned_task")
    owner = models.ForeignKey(User, related_name="task_owner")
    entrance = models.OneToOneField(Entrance, related_name="tasks")
    create_time = models.DateTimeField(auto_now_add=True)
    is_hide = models.BooleanField(default=False)

    def __unicode__(self):
        return self.entrance


class TaskMessageType(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.title


def get_message_file_path(instance, filename):
    today = datetime.today()
    if instance.attached_file:
        filename = "messages/%d_%d_%d/%s" % (today.year, today.month, today.day, str(filename))
    return filename


class TaskMessage(models.Model):
    message_type = models.ForeignKey(TaskMessageType, related_name="messages")
    message_content = models.TextField(default="")
    attached_file = models.FileField(null=True, upload_to=get_message_file_path)
    form_user = models.ForeignKey(User, related_name="fusers")
    to_user = models.ForeignKey(User, related_name="tusers")
    message_time = models.DateTimeField(auto_now_add=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    seen = models.BooleanField(default=False)
    seen_time = models.DateTimeField(null=True)
    task = models.ForeignKey(Task, related_name="messages")

    def __unicode__(self):
        return "%s -> %s: %s" % (self.form_user, self.to_user, self.message_type)


def get_readydata_file_path(instance, filename):
    if instance.file:
        unique_key = instance.task.entrance.unique_key
        extension = instance.file.path.split('.')[-1]
        return os.path.join("ReadyData", str(unique_key), str(instance.entrance_booklet_detail.id) + '.' + extension)
    else:
        return filename


class ReadyData(models.Model):
    task = models.ForeignKey(Task, related_name="r_data")
    entrance_booklet_detail = models.ForeignKey(EntranceBookletDetail, related_name="r_data")
    upload_time = models.DateTimeField(null=True)
    file = models.FileField(null=True, upload_to=get_readydata_file_path)

    def save(self, *args, **kwargs):
        try:
            this = ReadyData.objects.get(id=self.id)
            if this.file != self.file:
                this.file.delete(save=False)

        except:
            pass

        super(ReadyData, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        storage, path = self.file.storage, self.file.path
        super(ReadyData, self).delete(*args, **kwargs)
        storage.delete(path)

    def __unicode__(self):
        return u"%s (%s)" % (self.task, self.entrance_booklet_detail)

    class Meta:
        unique_together = ('task', 'entrance_booklet_detail')