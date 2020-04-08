from django.http import JsonResponse
from offline_app.models import *
from offline_app.views import request_handler

METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"


def sync_offline_server_with_online(request):
    if request.method != "GET":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    all_saved_request = SavedUsedAPIs.objects.all().order_by("id")

    for saved_request in  all_saved_request:
        response = request_handler(saved_request.api_method, saved_request.api_url, saved_request.payload.replace("\'", "\""))
        if response[0]['response_code'] == 2:
            saved_request.delete()

    return JsonResponse({'response_code': 2})
