from django import template
from gridfs import GridFS

from admin.Forms.DEHelpForms import HELP_LANGUAGE
from admin.Forms.DEJobForms import RejectReasonChoices, TYPE_FILE_CONTENT
from admin.Forms.UserManagementForms import USER_CHECKER_STATE_TYPE
from main.models_functions import connectToMongo

register = template.Library()

__author__ = 'abolfazl'


@register.filter(name="ereject_res", takes_context=True)
def entrance_reject_resolve(value):
    for item in RejectReasonChoices:
        if item[0] == value:
            return item[1]

    return ""


@register.filter(name="ftype_res", takes_context=True)
def entrance_file_type(value):
    for item in TYPE_FILE_CONTENT:
        if item[0] == value:
            return item[1]

    return ""


@register.filter(name="chkstate_res", takes_context=True)
def checker_state_type(value):
    for item in USER_CHECKER_STATE_TYPE:
        if item[0] == value:
            return item[1]

    return ""


@register.filter(name="gfs_base64", takes_context=True)
def gridfs_image(img):
    db = connectToMongo()

    fs = GridFS(db)
    fs_obj = fs.get(img)

    return fs_obj.read().encode('base64')


@register.filter(name="help_lang_res", takes_context=True)
def help_lang_type(value):
    for item in HELP_LANGUAGE:
        if item[0] == value:
            return item[1]

    return ""


@register.filter(name="dict_value", takes_context=True)
def dict_value(d, key):
    if isinstance(d, dict) and key in d:
        return d[key]

    return ""

