# coding=utf-8
__author__ = 'abolfazl'

from django.contrib.auth.models import User, Group

# find groups
admin_group = Group.objects.get(name='administrator')
master_operator_group = Group.objects.get(name='master_operator')
picture_creator_group = Group.objects.get(name='picture_creator')
editor_group = Group.objects.get(name='editor')
simple_group = Group.objects.get(name='simple')

# create users
admin_user = User.objects.get(username='ab***eh')
admin_user = User.objects.create_user('ab****eh', email='****@gmail.com', password='****')
admin_user.first_name = '****'
admin_user.last_name = '****'
admin_user.is_staff = True
admin_user.is_active = True
admin_user.groups = [admin_group, master_operator_group, simple_group]
admin_user.save()

master_user = User.objects.create_user('masteropt', email='master@gmail.com', password='master@102')
master_user.first_name = 'master'
master_user.last_name = ''
master_user.is_staff = True
master_user.is_active = True
master_user.groups = [master_operator_group, simple_group]
master_user.save()


editor_user = User.objects.create_user('rmoh***', email='****', password='****')
editor_user.first_name = '****'
editor_user.last_name = '****'
editor_user.is_staff = False
editor_user.is_active = True
editor_user.groups = [editor_group, simple_group]
editor_user.save()
