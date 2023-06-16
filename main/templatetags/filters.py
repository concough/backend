# coding=utf-8
import pytz
from django import template
import jdatetime
import datetime
from admin.Helpers.static_values import JALALI_MONTHES, QuestionAnswerKeyChoicesDict
from main.Helpers.model_static_values import ENTRANCE_SALE_COST_TYPES

register = template.Library()

__author__ = 'abolfazl'


@register.filter(name="jalali", takes_context=True)
def tojalali(value):
    jalal_date = jdatetime.datetime.fromgregorian(day=value.day, month=value.month, year=value.year)
    return "%s %s %s" % (jalal_date.day, JALALI_MONTHES[jalal_date.month - 1],
                         jalal_date.year)


@register.filter(name="jalalitime", takes_context=True)
def tojalalitime(value):
    timezone = pytz.timezone("Asia/Tehran")

    local2 = value.replace(tzinfo=pytz.utc).astimezone(timezone)
    jalal_date = jdatetime.datetime.fromgregorian(datetime=local2)

    return "%s %s %s ساعت %s:%s" % ( jalal_date.day, JALALI_MONTHES[jalal_date.month - 1],
                         jalal_date.year, jalal_date.hour, jalal_date.minute,)


@register.filter(name="jalalimonth", takes_context=True)
def tojalalimonth(value):
    return JALALI_MONTHES[value - 1]


@register.filter(name="qa_to_text", takes_context=True)
def question_answer_to_text(value):
    return QuestionAnswerKeyChoicesDict[str(value)]


@register.filter(name="entrance_sale_cost_value", takes_context=True)
def entrance_sale_cost_value(value):
    for item in ENTRANCE_SALE_COST_TYPES:
        if item[0] == value:
            return item[1]


@register.filter(name="multiply", takes_context=True)
def multiply(value, arg):
    return value * arg


@register.filter(name="addme", takes_context=True)
def add(value, arg):
    return value + int(arg)

