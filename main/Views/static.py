import os
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from dataentry.models import ReadyData, TaskMessage
from digikunkor import settings

__author__ = 'abolfazl'


@login_required
def serve_media(request, path=''):
    # get which media requested
    if path and path != '':
        if '..' not in path.split(os.path.sep):
            fpath = path.split(os.path.sep)[0]
            if fpath:
                fullpath = os.path.join(settings.MEDIA_ROOT, path)

                if fpath == 'Esets':
                    # entrance set picture requested
                    response = HttpResponse()
                    del response['content-type']
                    response['X-Sendfile'] = fullpath
                    return response

                elif fpath == 'Qs':
                    user = request.user
                    groups = [item.name for item in user.groups.all()]
                    if 'administrator' in groups or 'master_operator' in groups:
                        response = HttpResponse()
                        del response['content-type']
                        response['X-Sendfile'] = fullpath
                        return response

                elif fpath == 'ReadyData':
                    user = request.user
                    groups = [item.name for item in user.groups.all()]

                    # Get task record
                    rd = get_object_or_404(ReadyData, file=path)
                    task = rd.task
                    has_access = False
                    if task.owner == user or task.user == user:
                        has_access = True

                    if 'administrator' in groups or has_access:
                        response = HttpResponse()
                        del response['content-type']
                        response['X-Sendfile'] = fullpath
                        return response

                elif fpath == 'messages':
                    user = request.user
                    msg = get_object_or_404(TaskMessage, attached_file=path)
                    if msg.form_user == user or msg.to_user == user:
                        response = HttpResponse()
                        del response['content-type']
                        response['X-Sendfile'] = fullpath
                        return response

    return HttpResponseNotFound()
