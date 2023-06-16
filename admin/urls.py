from admin.Views.de_app_manage import app_version_del, app_version_list, bug_reports_list, bug_report_del, \
    bug_report_reply
from admin.Views.de_basic_info import organization_del, organization_list, entrance_type_list, entrance_type_del, \
    examination_group_list, examination_group_del, entrance_set_del, entrance_set_list, entrance_lesson_type_list, \
    entrance_lesson_detail_list, entrance_lesson_del, entrance_lesson_add, entrance_set_add, entrance_subset_del, \
    entrance_subset_list, taskmessage_type_del, taskmessage_type_list, entrance_set_edit, \
    organization_edit
from admin.Views.de_contents import content_dashboard, content_quotes_category_list, content_quotes_category_del, \
    content_quotes_list, content_quotes_add, content_quotes_del, content_quotes_edit, content_quotes_publish_app, \
    content_quotes_publish_blog
from admin.Views.de_costs_manage import entrance_sale_data_list, entrance_tags_sale_data_list
from admin.Views.de_entrance import entrance_list, entrance_booklets_list, entrance_del, entrance_add, \
    entrance_booklet_add, entrance_booklet_detail_add, entrance_question_list, entrance_question_generate_all, \
    entrance_question_picture_list, entrance_question_picture_del, entrance_extra_data_add, entrance_extra_data_clear, \
    entrance_booklet_detail_del, entrance_booklet_del, create_package, list_package, reset_package, delete_package, \
    entrance_question_file_change, entrance_question_picture_ajax, entrance_create_job, entrance_change_is_editing, \
    entrance_jobs_finished_list, entrance_multi_list, entrance_multi_add, entrance_multi_del, entrance_multi_unpublish, \
    entrance_multi_publish, entrance_question_tags_list, entrance_question_tags_add, entrance_question_tags_del, \
    entrance_question_tags_file, entrance_tags_package_list, entrance_tag_package_publish
from admin.Views.de_entrance_factors import entrance_factor_list, entrance_factor_view, entrance_factor_del
from admin.Views.de_general import get_tags_ajax
from admin.Views.de_helps import helps_sections_list, helps_sections_edit, helps_sections_del, helps_sections_lang_list, \
    helps_sections_lang_del, helps_sections_lang_subs_list, helps_sections_lang_subs_add, helps_sections_lang_subs_edit, \
    helps_sections_lang_subs_del, helps_sections_lang_subs_available, helps_sections_lang_subs_unavailable, \
    helps_sections_lang_subs_device_add, helps_sections_lang_subs_device_edit, helps_sections_lang_subs_device_del
from admin.Views.de_jobs import entrance_job_list, entrance_job_detail, entrance_job_detail_start_type, \
    entrance_job_detail_download_orig_file, entrance_job_detail_type_done, entrance_job_detail_download_term_file, \
    entrance_job_detail_wait_for_check, entrance_job_detail_start_check, entrance_job_detail_check_done, \
    entrance_job_detail_task_accepted, entrance_job_detail_start_check2, entrance_job_detail_wait_for_recheck, \
    entrance_job_detail_send_for_finance, entrance_job_detail_task_rejected, entrance_job_detail_reject_and_retype, \
    entrance_job_tasks_news_list, entrance_job_detail_choose_typist, entrance_job_tasks_typist_state, \
    entrance_job_finance, entrance_job_finance_accounting, entrance_job_finance_pay_off, \
    entrance_job_finance_accounting_list, entrance_job_editor_finance, entrance_job_finish, \
    entrance_job_detail_type_upload_file, entrance_job_detail_download_main_term_file, entrance_job_download_main_file, \
    entrance_job_detail_start_check2_wrong_file, entrance_job_detail_start_check_wrong_file, \
    entrance_job_detail_continue_check, entrance_job_checker_finance, entrance_job_settings_checkers_cost, \
    entrance_job_checker_finance_pay_off, entrance_job_detail_cancel_type, entrance_job_finance_accounting_all
from admin.Views.de_payment_manage import payment_provider_list, payment_provider_del, \
    payment_provider_add
from admin.Views.de_settings import users_list, users_add, users_activate, users_deactivate, users_financial_list, \
    users_financial_edit, users_financial_add, users_financial_del, users_edit, users_checkers_state_list
from admin.Views.home import dashboard
from admin.Views.messages import message_list, message_new, message_reply, message_seen
from admin.Views.reports import reports_general, reports_campaign, reports_campaign_add, reports_campaign_del, \
    reports_campaign_sync, reports_campaign_chart, reports_campaign_show
from admin.Views.tasks import task_list, task_add, task_del, task_details

__author__ = 'abolfazl'
from django.conf.urls import url

urlpatterns = (
    url(r'^de/basic_info/orgs/del/(?P<pk>\d+)$', organization_del, name="admin.de_basic_info.organization.del"),
    url(r'^de/basic_info/orgs/edit/(?P<pk>\d+)$', organization_edit, name="admin.de_basic_info.organization.edit"),
    url(r'^de/basic_info/orgs/$', organization_list, name="admin.de_basic_info.organization"),
    url(r'^de/basic_info/etypes/del/(?P<pk>\d+)$', entrance_type_del, name="admin.de_basic_info.entrance_type.del"),
    url(r'^de/basic_info/etypes/$', entrance_type_list, name="admin.de_basic_info.entrance_type"),
    url(r'^de/basic_info/egroups/del/(?P<pk>\d+)$', examination_group_del,
        name="admin.de_basic_info.examination_group.del"),
    url(r'^de/basic_info/egroups/$', examination_group_list, name="admin.de_basic_info.examination_group"),
    url(r'^de/basic_info/esets/edit/(?P<pk>\d+)$', entrance_set_edit, name="admin.de_basic_info.entrance_set.edit"),
    url(r'^de/basic_info/esets/del/(?P<pk>\d+)$', entrance_set_del, name="admin.de_basic_info.entrance_set.del"),
    url(r'^de/basic_info/esets/add/$', entrance_set_add, name="admin.de_basic_info.entrance_set.add"),
    url(r'^de/basic_info/esets/$', entrance_set_list, name="admin.de_basic_info.entrance_set"),
    url(r'^de/basic_info/esubsets/del/(?P<pk>\d+)$', entrance_subset_del,
        name="admin.de_basic_info.entrance_subset.del"),
    url(r'^de/basic_info/esubsets/$', entrance_subset_list, name="admin.de_basic_info.entrance_subset"),
    url(r'^de/basic_info/elessons/del/(?P<pk>\d+)$', entrance_lesson_del,
        name="admin.de_basic_info.entrance_lesson.del"),
    url(r'^de/basic_info/elessons/(?P<pk>\d+)/add/$', entrance_lesson_add,
        name="admin.de_basic_info.entrance_lesson.add"),
    url(r'^de/basic_info/elessons/(?P<pk>\d+)$', entrance_lesson_detail_list,
        name="admin.de_basic_info.entrance_lesson.details"),
    url(r'^de/basic_info/elessons/$', entrance_lesson_type_list, name="admin.de_basic_info.entrance_lesson"),
    url(r'^de/basic_info/taskmsgtypes/del/(?P<pk>\d+)$', taskmessage_type_del,
        name="admin.de_basic_info.task_message_type.del"),
    url(r'^de/basic_info/taskmsgtypes/$', taskmessage_type_list, name="admin.de_basic_info.task_message_type"),
    url(r'^de/basic_info/$', organization_list, name="admin.de_basic_info"),

    url(r'^de/costs/entrance_tags/?$', entrance_tags_sale_data_list, name="admin.costs.entrance_tags_sale_data"),
    url(r'^de/costs/entrance/?$', entrance_sale_data_list, name="admin.costs.entrance_sale_data"),
    url(r'^de/costs/?$', entrance_sale_data_list, name="admin.costs"),

    url(r'^de/entrance/(?P<pk>\d+)/detail/(?P<bd_id>\d+)/tags/publish$', entrance_tag_package_publish,
        name="admin.de_entrance.tags.packages.publish"),
    url(r'^de/entrance/(?P<pk>\d+)/tags/packages/(?P<p_id>\d+)/del/?$', entrance_tags_package_list,
        name="admin.de_entrance.tags.packages.del"),
    url(r'^de/entrance/(?P<pk>\d+)/tags/packages/$', entrance_tags_package_list,
        name="admin.de_entrance.tags.packages.list"),
    url(r'^de/entrance/add/$', entrance_add, name="admin.de_entrance.add"),
    url(r'^de/entrance/del/(?P<pk>\d+)$', entrance_del, name="admin.de_entrance.del"),
    url(r'^de/entrance/publish/(?P<pk>\d+)/create/$', create_package, name="admin.de_entrance.publish"),
    url(r'^de/entrance/publish/(?P<pk>\d+)/reset/$', reset_package, name="admin.de_entrance.publish.reset"),
    url(r'^de/entrance/publish/del/(?P<pk>\d+)$', delete_package, name="admin.de_entrance.publish.del"),
    url(r'^de/entrance/publish/(?P<pk>\d+)$', list_package, name="admin.de_entrance.publish.list"),
    url(r'^de/entrance/(?P<pk>\d+)/booklets/add/$', entrance_booklet_add, name="admin.de_entrance.booklets.add"),
    url(r'^de/entrance/(?P<pk>\d+)/booklets/$', entrance_booklets_list, name="admin.de_entrance.booklets.list"),
    url(r'^de/entrance/(?P<pk>\d+)/extradata/$', entrance_booklets_list, name="admin.de_entrance.booklets.extra_data"),
    url(r'^de/entrance/(?P<pk>\d+)/extradata/add/$', entrance_extra_data_add, name="admin.de_entrance.extra_data.add"),
    url(r'^de/entrance/(?P<pk>\d+)/extradata/clear/$', entrance_extra_data_clear,
        name="admin.de_entrance.extra_data.clear"),
    url(r'^de/entrance/(?P<pk>\d+)$', entrance_booklets_list, name="admin.de_entrance.booklets"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/del/$', entrance_booklet_del, name="admin.de_entrance.booklets.del"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/lesson/add/$', entrance_booklet_detail_add,
        name="admin.de_entrance.booklets.detail.add"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/lesson/del/$', entrance_booklet_detail_del,
        name="admin.de_entrance.booklets.detail.del"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/questions/(?P<qid>\d+)/tags/(?P<tid>\d+)/del/?$',
        entrance_question_tags_del,
        name="admin.de_entrance.tags.del"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/questions/$', entrance_question_list,
        name="admin.de_entrance.questions.list"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/tags/file/?$', entrance_question_tags_file,
        name="admin.de_entrance.tags.file"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/tags/add/?$', entrance_question_tags_add,
        name="admin.de_entrance.tags.add"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/tags/?$', entrance_question_tags_list,
        name="admin.de_entrance.tags.list"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/questions/file/$', entrance_question_file_change,
        name="admin.de_entrance.questions.file"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/pquestions/ajax/$', entrance_question_picture_ajax,
        name="admin.de_entrance.pquestions.ajax"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/pquestions/$', entrance_question_picture_list,
        name="admin.de_entrance.pquestions.list"),
    url(r'^de/entrance/booklets/(?P<pk>\d+)/questions/generate/$', entrance_question_generate_all,
        name="admin.de_entrance.questions.generate"),
    url(r'^de/entrance/booklets/pquestions/(?P<pk>\d+)/del/$', entrance_question_picture_del,
        name="admin.de_entrance.pquestions.del"),
    url(r'^de/entrance/(?P<pk>\d+)/editing/(?P<state>\w+)/?$', entrance_change_is_editing,
        name="admin.de_entrance.is_editing.change"),
    # url(r'^de/entrance/(?P<pk>\d+)/createjob/?$', entrance_create_job, name="admin.de_entrance.create_job"),
    url(r'^de/entrance/createjob/?$', entrance_create_job, name="admin.de_entrance.create_job"),
    url(r'^de/entrance/jobs/finished/?$', entrance_jobs_finished_list, name="admin.de_entrance.jobs_finished"),
    url(r'^de/entrance/$', entrance_list, name="admin.de_entrance"),
    url(r'^de/entrancefactors/(?P<pk>\d+)$', entrance_factor_view, name="admin.de_entrance_factors.view"),
    url(r'^de/entrancefactors/(?P<pk1>\d+)/del/(?P<pk2>\d+)$', entrance_factor_del,
        name="admin.de_entrance_factors.del"),
    url(r'^de/entrancefactors/$', entrance_factor_list, name="admin.de_entrance_factors"),
    url(r'^de/tasks/add/$', task_add, name="admin.tasks.add"),
    url(r'^de/tasks/del/(?P<pk>\d+)$', task_del, name="admin.tasks.del"),
    url(r'^de/tasks/(?P<pk>\d+)$', task_details, name="admin.tasks.details"),

    url(r'^de/entrance_multi/add/$', entrance_multi_add, name="admin.de_entrance_multi.add"),
    url(r'^de/entrance_multi/(?P<pk>\d+)/del/$', entrance_multi_del, name="admin.de_entrance_multi.del"),
    url(r'^de/entrance_multi/(?P<pk>\d+)/unpublish/$', entrance_multi_unpublish,
        name="admin.de_entrance_multi.unpublish"),
    url(r'^de/entrance_multi/(?P<pk>\d+)/publish/$', entrance_multi_publish, name="admin.de_entrance_multi.publish"),
    url(r'^de/entrance_multi/$', entrance_multi_list, name="admin.de_entrance_multi"),

    url(r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/add/?$',
        helps_sections_lang_subs_add, name="admin.help_manage.sections.langs.subs.add"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/devices/(?P<device>\w+)/edit/?$',
        helps_sections_lang_subs_device_edit, name="admin.help_manage.sections.langs.subs.devices.edit"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/devices/(?P<device>\w+)/del/?$',
        helps_sections_lang_subs_device_del, name="admin.help_manage.sections.langs.subs.devices.del"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/devices/add/?$',
        helps_sections_lang_subs_device_add, name="admin.help_manage.sections.langs.subs.devices.add"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/unavailable/?$',
        helps_sections_lang_subs_unavailable, name="admin.help_manage.sections.langs.subs.unavail"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/available/?$',
        helps_sections_lang_subs_available, name="admin.help_manage.sections.langs.subs.avail"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/del/?$',
        helps_sections_lang_subs_del, name="admin.help_manage.sections.langs.subs.del"),
    url(
        r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/(?P<sub_unique_id>[0-9a-fA-F]{32})/edit/?$',
        helps_sections_lang_subs_edit, name="admin.help_manage.sections.langs.subs.edit"),
    url(r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/subs/?$', helps_sections_lang_subs_list,
        name="admin.help_manage.sections.langs.subs"),
    url(r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/(?P<lang>\w+)/del/?$', helps_sections_lang_del,
        name="admin.help_manage.sections.langs.del"),
    url(r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/langs/?$', helps_sections_lang_list,
        name="admin.help_manage.sections.langs.list"),
    url(r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/del/?$', helps_sections_del,
        name="admin.help_manage.sections.del"),
    url(r'^de/helps/sections/(?P<unique_id>[0-9a-fA-F]{32})/edit/?$', helps_sections_edit,
        name="admin.help_manage.sections.edit"),
    url(r'^de/helps/sections/?$', helps_sections_list, name="admin.help_manage.sections"),

    url(r'^de/jobs/entrances/typists/?$', entrance_job_tasks_typist_state, name="admin.de_jobs.entrance.typists"),
    url(r'^de/jobs/entrances/news/?$', entrance_job_tasks_news_list, name="admin.de_jobs.entrance.news.list"),
    url(r'^de/jobs/entrances/upload_type/?$', entrance_job_detail_type_upload_file,
        name="admin.de_jobs.entrance.task.upload_type"),
    url(r'^de/jobs/entrances/check_done/?$', entrance_job_detail_check_done,
        name="admin.de_jobs.entrance.task.check_done"),
    url(r'^de/jobs/entrances/task_accepted/?$', entrance_job_detail_task_accepted,
        name="admin.de_jobs.entrance.task.accepted"),
    url(r'^de/jobs/entrances/task_rejected/?$', entrance_job_detail_task_rejected,
        name="admin.de_jobs.entrance.task.rejected"),
    url(r'^de/jobs/entrances/send_finance/?$', entrance_job_detail_send_for_finance,
        name="admin.de_jobs.entrance.task.send_finance"),
    url(r'^de/jobs/entrances/choost_typist/?$', entrance_job_detail_choose_typist,
        name="admin.de_jobs.entrance.task.choose_typist"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/continue_check/?$',
        entrance_job_detail_continue_check, name="admin.de_jobs.entrance.task.continue_check"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/check2_wrong/?$',
        entrance_job_detail_start_check2_wrong_file, name="admin.de_jobs.entrance.task.check2_wrong"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/check_wrong/?$',
        entrance_job_detail_start_check_wrong_file, name="admin.de_jobs.entrance.task.check_wrong"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/reject_retype/?$',
        entrance_job_detail_reject_and_retype, name="admin.de_jobs.entrance.task.reject_retype"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/start_check2/?$',
        entrance_job_detail_start_check2, name="admin.de_jobs.entrance.task.start_check2"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/start_check/?$',
        entrance_job_detail_start_check, name="admin.de_jobs.entrance.task.start_check"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/wait_for_recheck/?$',
        entrance_job_detail_wait_for_recheck, name="admin.de_jobs.entrance.task.wait_for_recheck"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/wait_for_check/?$',
        entrance_job_detail_wait_for_check, name="admin.de_jobs.entrance.task.wait_for_check"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/done_type/?$',
        entrance_job_detail_type_done, name="admin.de_jobs.entrance.task.done_type"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/start_type/?$',
        entrance_job_detail_start_type, name="admin.de_jobs.entrance.task.start_type"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/download/orig/?$',
        entrance_job_detail_download_orig_file, name="admin.de_jobs.entrance.task.download_orig"),
    url(
        r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/download/main_term/?$',
        entrance_job_detail_download_main_term_file, name="admin.de_jobs.entrance.task.download_main_term"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/download/term/?$',
        entrance_job_detail_download_term_file, name="admin.de_jobs.entrance.task.download_term"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/cancel_type/?$',
        entrance_job_detail_cancel_type, name="admin.de_jobs.entrance.task.cancel_type"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/details/(?P<detail_id>[0-9a-fA-F]{32})/?$',
        entrance_job_detail, name="admin.de_jobs.entrance.detail_with_id"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/download/main/?$', entrance_job_download_main_file,
        name="admin.de_jobs.entrance.download_main_file"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/finish/?$', entrance_job_finish,
        name="admin.de_jobs.entrance.finish"),
    url(r'^de/jobs/entrances/(?P<unique_id>[0-9a-fA-F]{32})/?$', entrance_job_detail,
        name="admin.de_jobs.entrance.detail"),
    url(r'^de/jobs/entrances/?$', entrance_job_list, name="admin.de_jobs.entrance.list"),
    url(r'^de/jobs/finance/list/entrances/?$', entrance_job_finance_accounting_list,
        name="admin.de_jobs.finance.list.entrances"),
    url(
        r'^de/jobs/finance/(?P<unique_id>[0-9a-fA-F]{32})/entrances/(?P<detail_id>[0-9a-fA-F]{32})/accounting/(?P<user_id>\d+)/?$',
        entrance_job_finance_accounting, name="admin.de_jobs.finance.entrance.accounting"),
    url(r'^de/jobs/finance/entrances/accounting/(?P<user_id>\d+)/all/?$', entrance_job_finance_accounting_all,
        name="admin.de_jobs.finance.entrance.accounting_all"),
    url(r'^de/jobs/finance/entrances/checker_pay_off/?$', entrance_job_checker_finance_pay_off,
        name="admin.de_jobs.finance.entrance.checker_pay_off"),
    url(r'^de/jobs/finance/entrances/pay_off/?$', entrance_job_finance_pay_off,
        name="admin.de_jobs.finance.entrance.pay_off"),
    url(r'^de/jobs/finance/entrances/checkers/?$', entrance_job_checker_finance,
        name="admin.de_jobs.finance.entrances.checkers"),
    url(r'^de/jobs/finance/entrances/editors/?$', entrance_job_editor_finance,
        name="admin.de_jobs.finance.entrances.editors"),
    url(r'^de/jobs/finance/entrances/?$', entrance_job_finance, name="admin.de_jobs.finance.entrances"),
    url(r'^de/jobs/finance/?$', entrance_job_finance, name="admin.de_jobs.finance"),
    url(r'^de/jobs/settings/checker_cost/?$', entrance_job_settings_checkers_cost,
        name="admin.de_jobs.settings.checker_cost"),
    url(r'^de/jobs/settings/?$', entrance_job_settings_checkers_cost, name="admin.de_jobs.settings"),
    url(r'^de/messages/(?P<pk>\d+)/new/$', message_new, name="admin.messages.new"),
    url(r'^de/messages/(?P<pk>\d+)/reply/$', message_reply, name="admin.messages.reply"),
    url(r'^de/messages/(?P<pk>\d+)/seen/$', message_seen, name="admin.messages.seen"),
    url(r'^de/messages/$', message_list, name="admin.messages"),
    url(r'^de/settings/$', users_list, name="admin.de_settings"),
    url(r'^de/settings/users/checker_state/?$', users_checkers_state_list,
        name="admin.de_settings.user_mgmt.checker_state"),
    url(r'^de/settings/users/$', users_list, name="admin.de_settings.user_mgmt"),
    url(r'^de/settings/users/add/$', users_add, name="admin.de_settings.user_mgmt.add"),
    url(r'^de/settings/users/(?P<pk>\d+)/edit/$', users_edit, name="admin.de_settings.user_mgmt.edit"),
    url(r'^de/settings/users/(?P<pk>\d+)/activate/$', users_activate, name="admin.de_settings.user_mgmt.activate"),
    url(r'^de/settings/users/(?P<pk>\d+)/deactivate/$', users_deactivate,
        name="admin.de_settings.user_mgmt.deactivate"),
    url(r'^de/settings/ufinancial/$', users_financial_list, name="admin.de_settings.user_mgmt.financial"),
    url(r'^de/settings/ufinancial/add/$', users_financial_add, name="admin.de_settings.user_mgmt.financial.add"),
    url(r'^de/settings/ufinancial/(?P<pk>\d+)/edit/$', users_financial_edit,
        name="admin.de_settings.user_mgmt.financial.edit"),
    url(r'^de/settings/ufinancial/(?P<pk>\d+)/del/$', users_financial_del,
        name="admin.de_settings.user_mgmt.financial.del"),
    url(r'^de/app_manage/bugs_report/(?P<pk>\d+)/reply/?$', bug_report_reply,
        name="admin.app_manage.bugs_report.reply"),
    url(r'^de/app_manage/bugs_report/(?P<pk>\d+)/del/?$', bug_report_del, name="admin.app_manage.bugs_report.del"),
    url(r'^de/app_manage/bugs_report/?$', bug_reports_list, name="admin.app_manage.bugs_report.list"),
    url(r'^de/app_manage/versions/(?P<pk>\d+)/del/?$', app_version_del, name="admin.app_manage.versions.del"),
    url(r'^de/app_manage/versions/?$', app_version_list, name="admin.app_manage.versions.list"),
    url(r'^de/app_manage/versions/?$', app_version_list, name="admin.app_manage.versions"),
    url(r'^de/app_manage/$', app_version_list, name="admin.app_manage"),
    url(r'^de/settings/payment_manage/providers/add/?$', payment_provider_add,
        name="admin.payment_manage.providers.add"),
    url(r'^de/settings/payment_manage/providers/(?P<pk>\d+)/del/?$', payment_provider_del,
        name="admin.payment_manage.providers.del"),
    url(r'^de/settings/payment_manage/providers/?$', payment_provider_list, name="admin.payment_manage.providers"),
    url(r'^de/settings/payment_manage/$', payment_provider_list, name="admin.payment_manage"),
    url(r'^de/reports/campaigns/(?P<unique_id>[0-9a-fA-F]{32})/chart/?$', reports_campaign_chart,
        name="admin.reports.campaign.chart"),
    url(r'^de/reports/campaigns/(?P<unique_id>[0-9a-fA-F]{32})/show/?$', reports_campaign_show,
        name="admin.reports.campaign.show"),
    url(r'^de/reports/campaigns/(?P<unique_id>[0-9a-fA-F]{32})/del/?$', reports_campaign_del,
        name="admin.reports.campaign.del"),
    url(r'^de/reports/campaigns/sync/?$', reports_campaign_sync, name="admin.reports.campaign.sync"),
    url(r'^de/reports/campaigns/add/?$', reports_campaign_add, name="admin.reports.campaign.add"),
    url(r'^de/reports/campaigns/$', reports_campaign, name="admin.reports.campaign"),
    url(r'^de/reports/general/$', reports_general, name="admin.reports.general"),
    url(r'^de/reports/$', reports_general, name="admin.reports"),
    url(r'^de/reports/$', reports_general, name="admin.reports"),
    url(r'^de/contents/quotes/categories/(?P<pk>\d+)/del/?$', content_quotes_category_del,
        name="admin.content_mgm.quotes.categories.del"),
    url(r'^de/contents/quotes/categories/?$', content_quotes_category_list, name="admin.content_mgm.quotes.categories"),
    url(r'^de/contents/quotes/(?P<pk>\d+)/publish/app/?$', content_quotes_publish_app,
        name="admin.content_mgm.quotes.publish.app"),
    url(r'^de/contents/quotes/(?P<pk>\d+)/publish/blog/?$', content_quotes_publish_blog,
        name="admin.content_mgm.quotes.publish.blog"),
    url(r'^de/contents/quotes/(?P<pk>\d+)/edit/?$', content_quotes_edit, name="admin.content_mgm.quotes.edit"),
    url(r'^de/contents/quotes/(?P<pk>\d+)/del/?$', content_quotes_del, name="admin.content_mgm.quotes.del"),
    url(r'^de/contents/quotes/add/?$', content_quotes_add, name="admin.content_mgm.quotes.add"),
    url(r'^de/contents/quotes/?$', content_quotes_list, name="admin.content_mgm.quotes"),
    url(r'^de/contents/dashboard/?$', content_dashboard, name="admin.content_mgm.dashboard"),
    url(r'^de/contents/?$', content_dashboard, name="admin.content_mgm"),
    url(r'^de/tags/?$', get_tags_ajax, name="admin.tags"),
    url(r'^$', dashboard, name="admin.home"),
)
