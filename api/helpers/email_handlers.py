from django.core.mail.message import EmailMultiAlternatives
from django.template.context import RequestContext
from django.template.loader import render_to_string

__author__ = 'abolfazl'


def send_email(subject, _from, _to, data, template_name, request):
    template_html = 'emails/%s.html' % template_name
    template_text = 'emails/%s.txt' % template_name

    try:
        text_content = render_to_string(template_text, data)
        html_content = render_to_string(template_html, RequestContext(request, data))

        msg = EmailMultiAlternatives(subject, text_content, _from, _to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception, exc:
        # Log error message
        print exc
        pass