from django.http import JsonResponse
import json
from offline_app.models import *
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.db import IntegrityError
from offline_app.views import create_new_request_for_online_api
from namak_offline.settings import BASE_ONLINE_SERVER_API_URL

METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
CASH_ERROR = "خطای صندوق"
NO_CASH_ERROR = "صندوقی وجود ندارد."


def get_today_cash(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch']

    branch_obj = Branch.objects.get(server_primary_key=branch_id)
    cash_obj = Cash.objects.filter(branch=branch_obj, is_close=0)
    if cash_obj.count() == 1:
        return JsonResponse({"response_code": 2, 'cash_id': cash_obj[0].id})
    elif cash_obj.count() == 0:
        return JsonResponse({"response_code": 3, 'error_message': NO_CASH_ERROR, "error_code": "NO_CASH"})
    else:
        return JsonResponse({"response_code": 3, 'error_message': CASH_ERROR})
