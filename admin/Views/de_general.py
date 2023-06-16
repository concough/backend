from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse

from main.models import Tags


@login_required
def get_tags_ajax(request):
    result = {}

    text = request.POST.get('title', None)
    if text is not None:
        tags = Tags.objects.filter(title__startswith=text)[:10]

        tags_list = []
        for item in tags:
            tags_list.append({
                'id': item.id,
                'title': item.title
            })

        result = {"status": "OK", "data": tags_list}
    else:
        result = {"status": "Error", "error_type": "INVALID"}
    return JsonResponse(result)