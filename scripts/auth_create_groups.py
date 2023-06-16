__author__ = 'abolfazl'

from django.contrib.auth.models import Group

admin_group = Group(name='administrator')
admin_group.save()

master_operator_group = Group(name='master_operator')
master_operator_group.save()

editor_group = Group(name='editor')
editor_group.save()

picture_creator_group = Group(name='picture_creator')
picture_creator_group.save()

simple_group = Group(name='simple')
simple_group.save()

# new in 96/09/22
admin_group = Group(name='check_in')
admin_group.save()

# new in 96/11/26
reporter = Group(name='reporter')
reporter.save()

# All applied at 96/11/27

# new in 96/11/28
job_supervisor = Group(name='job_supervisor')
job_supervisor.save()


# All applied at 96/12/10
content_provider = Group(name="content_provider")
content_provider.save()
