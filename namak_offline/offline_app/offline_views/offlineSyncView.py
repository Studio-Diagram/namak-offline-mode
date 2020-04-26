from django.http import JsonResponse
from offline_app.models import *
from offline_app.views import request_handler
from namak_offline.settings import BASE_ONLINE_SERVER_API_URL
import json
from offline_app.views import sync_reserve_with_server, sync_invoice_sale_with_server, sync_members_with_server, sync_cash_with_server

METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"


def sync_offline_server_with_online(request):
    if request.method != "GET":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    all_saved_request = SavedUsedAPIs.objects.all().order_by("id")

    print("Start Syncing members with Online.")
    for saved_request in all_saved_request:
        response = request_handler(saved_request.api_method, saved_request.api_url,
                                   saved_request.payload.replace("\'", "\""))
        if response[0]['response_code'] == 2:
            saved_request.delete()
    print("Finish Syncing members with Online.")

    print("Start Syncing Reserves with Online.")
    all_reserves_data = []
    have_to_delete = []
    all_reserve_objects = Reservation.objects.all()
    for reserve in all_reserve_objects:
        if reserve.server_primary_key:
            have_to_delete.append(reserve.server_primary_key)
        if reserve.is_delete:
            continue
        all_reserves_data.append(
            {
                "start_time": reserve.start_time,
                "end_time": reserve.end_time,
                "numbers": reserve.numbers,
                "reserve_date": reserve.reserve_date,
                "customer_name": reserve.customer_name,
                "phone": reserve.phone,
                "reserve_state": reserve.reserve_state,
                "branch_id": reserve.branch.server_primary_key,
                "is_delete": reserve.is_delete,
                "reserve_id": reserve.server_primary_key,
                "tables": [{
                    "table_id": table.table.server_primary_key
                } for table in ReserveToTables.objects.filter(reserve=reserve)]
            }
        )

    response = request_handler("POST", BASE_ONLINE_SERVER_API_URL + "api/offline/syncReservesFromOffline/",
                               json.dumps({"all_reserves_data": all_reserves_data, "have_to_delete": have_to_delete},
                                          indent=4, sort_keys=True, default=str))
    if response[0]['response_code'] == 2:
        all_reserve_objects.delete()
        sync_reserve_with_server()

    print("Finish Syncing Reserves with Online.")

    print("Start Syncing Invoice Sales with Online.")
    have_to_delete = []
    all_cashe_desk_objects = Cash.objects.all()
    all_cash_desk_data = [{
        "cash_offline_id": item.id,
        "cash_server_primary_key": item.server_primary_key,
        "created_date_time": item.created_date_time,
        "ended_date_time": item.ended_date_time,
        "income_report": item.income_report,
        "outcome_report": item.outcome_report,
        "event_tickets": item.event_tickets,
        "current_money_in_cash": item.current_money_in_cash,
        "employee": item.employee.phone if item.employee else "",
        "branch_server_primary_key": item.branch.server_primary_key,
        "is_close": item.is_close,
    } for item in all_cashe_desk_objects]

    all_invoice_objects = InvoiceSales.objects.all()
    all_invoices_data = [{
        "factor_number": invoice.factor_number,
        "created_time": invoice.created_time,
        "cash": invoice.cash,
        "pos": invoice.pos,
        "employee_discount": invoice.employee_discount,
        "tax": invoice.tax,
        "settlement_type": invoice.settlement_type,
        "table_name": invoice.table.name,
        "guest_numbers": invoice.guest_numbers,
        "total_price": invoice.total_price,
        "discount": invoice.discount,
        "tip": invoice.tip,
        "settle_time": invoice.settle_time,
        "is_settled": invoice.is_settled,
        "ready_for_settle": invoice.ready_for_settle,
        "server_primary_key": invoice.server_primary_key,
        "member_id": invoice.member.server_primary_key if invoice.member else 0,
        "member_card_number": invoice.member.card_number if invoice.member else 0,
        "cash_id": invoice.cash_desk.server_primary_key,
        "cash_offline_id": invoice.cash_desk.id,
        "table_id": invoice.table.server_primary_key,
        "branch_id": invoice.branch.server_primary_key,
        "is_do_not_want_order": invoice.is_do_not_want_order,
        "game_state": invoice.game_state,
        "is_delete": invoice.is_deleted,
        "delete_description": invoice.delete_description,
        "games_list": [{
            "member_id": game.game.member.server_primary_key if game.game.member else 0,
            "member_card_number": game.game.member if game.game.member.card_number else 0,
            "start_time": game.game.start_time,
            "end_time": game.game.end_time,
            "numbers": game.game.numbers,
            "points": game.game.points,
            "add_date": game.game.add_date,
            "server_primary_key_game": game.game.server_primary_key,
            "server_primary_key_invoice_to_game": game.server_primary_key
        } for game in InvoicesSalesToGame.objects.filter(invoice_sales=invoice)],
        "menu_items_list": [{
            "menu_item_id": menu_item.menu_item.server_primary_key,
            "numbers": menu_item.numbers,
            "description": menu_item.description,
            "is_print": menu_item.is_print,
            "server_primary_key_invoice_to_menu_item": menu_item.server_primary_key
        } for menu_item in InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice)]
    } for invoice in all_invoice_objects]

    response = request_handler("POST", BASE_ONLINE_SERVER_API_URL + "api/offline/syncInvoiceSalesFromOffline/",
                               json.dumps({"all_invoices_data": all_invoices_data, "have_to_delete": have_to_delete,
                                           "all_cash_desk_data": all_cash_desk_data},
                                          indent=4, sort_keys=True, default=str))

    if response[0]['response_code'] == 2:
        all_invoice_objects.delete()
        sync_members_with_server()
        sync_cash_with_server()
        sync_invoice_sale_with_server()

    print("Finish Syncing Invoice Sales with Online.")

    return JsonResponse({'response_code': 2})
