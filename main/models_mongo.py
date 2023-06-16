import uuid
import datetime
from mongoengine.document import DynamicDocument, DynamicEmbeddedDocument
from mongoengine.fields import StringField, DateTimeField, UUIDField, FileField, ListField

JOB_TYPES = (('ENTRANCE', 'Entrance Job'), )
JOB_STATUS = (('CREATED', 'Job created'),
              ('STARTED', 'Job has been started'),
              ('DONE', 'Job finished'))


class Job(DynamicDocument):
    job_type = StringField(max_length=30, choices=JOB_TYPES, required=True)
    #job_type = StringField(max_length=30, required=True)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True, default=datetime.datetime.now())
    status = StringField(max_length=20, required=True, choices=JOB_STATUS)
    #status = StringField(max_length=20, required=True)
    job_relate_uniqueid = UUIDField(unique_with="job_type")


class EntranceTask(DynamicEmbeddedDocument):
    task_unique_id = UUIDField(default=uuid.uuid4())
    state = StringField(max_length=50)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True, default=datetime.datetime.now())
    orig_file = FileField(required=False)
    term_file = FileField(required=False)
    logs = ListField()