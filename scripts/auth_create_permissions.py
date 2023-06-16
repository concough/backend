__author__ = 'abolfazl'

from django.contrib.auth.models import Group
from main.models import GlobalPermission


# find groups
admin_group = Group.objects.get(name='administrator')
master_operator_group = Group.objects.get(name='master_operator')
picture_creator_group = Group.objects.get(name='picture_creator')
editor_group = Group.objects.get(name='editor')


# assign permissions to group
dashboard_gp = GlobalPermission.objects.create(codename='de_dashboard', name='dashboard view')

admin_group.permissions.add(dashboard_gp)
master_operator_group.permissions.add(dashboard_gp)
editor_group.permissions.add(dashboard_gp)
picture_creator_group.permissions.add(dashboard_gp)

gp = GlobalPermission.objects.create(codename='de_basic_info', name='data entry basic information')
admin_group.permissions.add(gp)
gp = GlobalPermission.objects.create(codename='de_entrance_publish', name='data entry entrance publish')
admin_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_settings', name='Settings page')
admin_group.permissions.add(gp)
gp = GlobalPermission.objects.create(codename='de_settings.usermgmt', name='Settings User Management')
admin_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_entrance_detail', name='data entry entrance detail')
master_operator_group.permissions.add(gp)
gp = GlobalPermission.objects.create(codename='de_questions', name='data entry questions')
master_operator_group.permissions.add(gp)
gp = GlobalPermission.objects.create(codename='de_entrance_factors', name='data entry entrance factors')
master_operator_group.permissions.add(gp)
gp1 = GlobalPermission.objects.create(codename='de_view_tasks', name='data entry view tasks')
master_operator_group.permissions.add(gp1)
gp = GlobalPermission.objects.create(codename='de_create_task', name='data entry create task')
master_operator_group.permissions.add(gp)
gp2 = GlobalPermission.objects.create(codename='de_message_box', name='data entry message box')
master_operator_group.permissions.add(gp2)
gp3 = GlobalPermission.objects.create(codename='de_ready_data_list', name='data entry ready data list')
master_operator_group.permissions.add(gp3)

picture_creator_group.permissions.add(gp2)

editor_group.permissions.add(gp1)
editor_group.permissions.add(gp2)
editor_group.permissions.add(gp3)
gp = GlobalPermission.objects.create(codename='de_ready_data_upload', name='data entry ready data upload')
editor_group.permissions.add(gp)

# new 1
gp = GlobalPermission.objects.create(codename='de_app_manage', name='data entry manage app')
admin_group.permissions.add(gp)
gp = GlobalPermission.objects.create(codename='de_payment_manage', name='data entry manage payment')
admin_group.permissions.add(gp)


# new 2 -- 2/12/17
gp = GlobalPermission.objects.create(codename='de_entrance', name='all entrance permissions')
admin_group.permissions.add(gp)
master_operator_group.permissions.add(gp)

gp2 = GlobalPermission.objects.create(codename='de_entrance_basic_info', name='entrance basic information')
admin_group.permissions.add(gp2)
master_operator_group.permissions.add(gp2)

gp3 = GlobalPermission.objects.create(codename='de_settings.usermgmt.financial', name='user financial record')
admin_group.permissions.add(gp3)

# new 3 -- 96/09/22
gp = GlobalPermission.objects.create(codename='de_jobs', name='all jobs')
admin_group.permissions.add(gp)
master_operator_group.permissions.add(gp)
editor_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_jobs.entrance', name='all entrance jobs')
master_operator_group.permissions.add(gp)
editor_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_jobs.entrance.manage', name='entrance jobs manage')
master_operator_group.permissions.add(gp)


# until now added 961006

#new4 -- 96/10/02
check_in_group = Group.objects.get(name='check_in')

gp = GlobalPermission.objects.get(codename='de_dashboard')
check_in_group.permissions.add(gp)

gp = GlobalPermission.objects.get(codename='de_jobs')
check_in_group.permissions.add(gp)

gp = GlobalPermission.objects.get(codename='de_jobs.entrance')
check_in_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_jobs.finance', name='all jobs finance')
admin_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='reports', name='all reports')
admin_group.permissions.add(gp)

#new5 - 96/11/10
gp = GlobalPermission.objects.create(codename='de_helps', name='all helps')
admin_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='reports.campaign', name='all campaigns reports')
admin_group.permissions.add(gp)

reporter_group = Group.objects.get(name='reporter')
gp = GlobalPermission.objects.get(codename='de_dashboard')
reporter_group.permissions.add(gp)
gp = GlobalPermission.objects.get(codename='reports')
reporter_group.permissions.add(gp)
gp = GlobalPermission.objects.get(codename='reports.campaign')
reporter_group.permissions.add(gp)

# All applied at 96/11/27

# new in 96/11/28
job_supervisor_group = Group.objects.get(name='job_supervisor')

gp = GlobalPermission.objects.get(codename='de_dashboard')
job_supervisor_group.permissions.add(gp)

gp = GlobalPermission.objects.get(codename='de_jobs')
job_supervisor_group.permissions.add(gp)

gp = GlobalPermission.objects.get(codename='de_jobs.entrance')
job_supervisor_group.permissions.add(gp)

gp = GlobalPermission.objects.get(codename='de_jobs.entrance.manage')
job_supervisor_group.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_jobs.settings', name='jobs panel settings')
admin_group.permissions.add(gp)

# All applied at 96/12/10

# new in 96/12/21
content_provider = Group.objects.get(name="content_provider")

gp = GlobalPermission.objects.get(codename='de_dashboard')
content_provider.permissions.add(gp)

gp = GlobalPermission.objects.get(codename='de_helps')
content_provider.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_content_provide')
content_provider.permissions.add(gp)
admin_group.permissions.add(gp)

# All applied at 96/12/22

# new in 96/12/24
content_provider = Group.objects.get(name="content_provider")

gp = GlobalPermission.objects.create(codename='de_content_quotes', name="Quotes Content Providing")
content_provider.permissions.add(gp)

gp = GlobalPermission.objects.create(codename='de_content_quotes.manage', name="Manage Quotes Content Providing")
content_provider.permissions.add(gp)


# new in 98/03/18

master_operator_group = Group.objects.get(name='master_operator')

gp = GlobalPermission.objects.create(codename='de_costs_manage', name="Products Cost Management")
master_operator_group.permissions.add(gp)