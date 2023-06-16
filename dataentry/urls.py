from dataentry.Views.home import dashboard
from dataentry.Views.messages import message_list, message_reply, message_seen
from dataentry.Views.tasks import task_list, task_details, task_ready_data_upload
from django.conf.urls import url

__author__ = 'abolfazl'

urlpatterns = (url(r'^de/tasks/upload/(?P<pk>\d+)$', task_ready_data_upload, name="dataentry.tasks.details.uploadfile"),
               url(r'^de/tasks/(?P<pk>\d+)$', task_details, name="dataentry.tasks.details"),
               url(r'^de/tasks/$', task_list, name="dataentry.tasks"),
               url(r'^de/messages/(?P<pk>\d+)/reply/$', message_reply, name="dataentry.messages.reply"),
               url(r'^de/messages/(?P<pk>\d+)/seen/$', message_seen, name="dataentry.messages.seen"),
               url(r'^de/messages/$', message_list, name="dataentry.messages"),
               url(r'^$', dashboard, name="dataentry.home"),
               )
