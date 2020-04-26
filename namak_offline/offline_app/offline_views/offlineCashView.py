from django.http import JsonResponse
import json, datetime
from offline_app.models import *

METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
CASH_ERROR = "خطای صندوق"
NO_CASH_ERROR = "صندوقی وجود ندارد."
DATA_REQUIRE = "اطلاعات را به شکل کامل وارد کنید."
UNSETTLED_INVOICE = "فاکتور تسویه نشده وجود دارد."
DUPLICATE_CASH = 'دو صندوق باز وجود دارد. با تیم فنی تماس بگیرید.'


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


def close_cash(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    now = datetime.datetime.now()
    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch_id']
    username = rec_data['username']
    if 'night_report_inputs' not in rec_data.keys():
        night_report_inputs = {
            "current_money_in_cash": 0,
            "income_report": 0,
            "outcome_report": 0,
            "event_tickets": 0
        }
    else:
        night_report_inputs = rec_data['night_report_inputs']

    if not username:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    if night_report_inputs['income_report'] == "" or night_report_inputs['outcome_report'] == "" \
            or night_report_inputs['event_tickets'] == "" or night_report_inputs['current_money_in_cash'] == "":
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch_obj = Branch.objects.get(server_primary_key=branch_id)
    user_object = Employee.objects.filter(phone=username).first()
    current_cash = Cash.objects.filter(branch=branch_obj, is_close=0)

    if current_cash.count() == 1:
        all_invoices_from_this_cash = InvoiceSales.objects.filter(cash_desk=current_cash.first(), is_settled=False,
                                                                  is_deleted=False)
        if all_invoices_from_this_cash.count():
            return JsonResponse({"response_code": 3, 'error_msg': UNSETTLED_INVOICE})
        current_cash_obj = current_cash.first()
        current_cash_obj.is_close = 1
        current_cash_obj.employee = user_object
        current_cash_obj.ended_date_time = now
        current_cash_obj.current_money_in_cash = night_report_inputs['current_money_in_cash']
        current_cash_obj.income_report = night_report_inputs['income_report']
        current_cash_obj.outcome_report = night_report_inputs['outcome_report']
        current_cash_obj.event_tickets = night_report_inputs['event_tickets']
        current_cash_obj.save()
        return JsonResponse({"response_code": 2})
    else:
        return JsonResponse({"response_code": 3, 'error_msg': DUPLICATE_CASH})


def open_cash(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data.get('branch_id')

    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch_object = Branch.objects.get(server_primary_key=branch_id)
    Cash(branch=branch_object, server_primary_key=0).save()
    return JsonResponse({"response_code": 2})
