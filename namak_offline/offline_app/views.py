from django.db import IntegrityError
from django.http import JsonResponse
from offline_app.models import *
import requests, json, jdatetime
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from namak_offline import config

BASE_URL = config.BASE_URL
METHODE_NOT_ALLOWED = "This method is not allowed."
PAYLOAD_EMPTY = "Payload is empty!"
DATA_REQUIRE = "Data required!"
DUPLICATE_MEMBER_ENTRY = "DUPLICATE_MEMBER_ENTRY"
METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
TIME_NOT_IN_CORRECT_FORMAT = 'زمان را به حالت درستی وارد کنید.'
PRICE_PER_POINT_IN_GAME = 5000
DUPLICATE_CASH = 'دو صندوق باز وجود دارد. با تیم فنی تماس بگیرید.'
NO_CASH = 'صندوق بازی وجود ندارد.'
OLD_CASH = 'انقضای صندوق گذشته است.'
UNSETTLED_INVOICE = "فاکتور تسویه نشده وجود دارد."
BRANCH_ID = 1


def request_handler(method, url, payload=None):
    if method == "GET":
        r = requests.get(url)
        return json.loads(r.text), r.status_code
    elif method == "POST":
        r = requests.post(url, payload)
        return json.loads(r.text), r.status_code


def sync_members_with_server():
    last_member = Member.objects.all().last()
    response = request_handler("GET", BASE_URL + "api/offline/list/member/%d/%d/" % (last_member.server_primary_key, BRANCH_ID))
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['members']:
            new_member = Member(last_name=item['last_name'], card_number=item['card_number'],
                                server_primary_key=int(item['p_key']))
            new_member.save()

    print("Member Synchronization Complete.")


def create_new_request_for_online_api(api_url, method, payload):
    try:
        new_request = SavedUsedAPIs(
            api_url=api_url,
            api_method=method,
            payload=payload
        )
        new_request.save()

        return True
    except Exception as e:
        print(e)
        return False


@csrf_exempt
def create_member(request):
    if request.method != "POST":
        return JsonResponse({"status_code": 3, "error_msg": METHODE_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    payload = rec_data.get("payload")

    if not payload:
        return JsonResponse({"status_code": 3, "error_msg": PAYLOAD_EMPTY})

    method = payload.get('method')
    member_id = payload.get('member_primary_key')
    last_name = payload.get('last_name')
    card_number = payload.get('card_number')
    card_number = card_number.replace("؟", "")
    card_number = card_number.replace("٪", "")
    card_number = card_number.replace("?", "")
    card_number = card_number.replace("%", "")

    if not last_name:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not card_number:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    if method == "create":
        try:
            new_member = Member(
                last_name=last_name,
                card_number=card_number,
                server_primary_key=member_id
            )
            new_member.save()
        except IntegrityError as e:
            if 'unique constraint' in e.args[0]:
                return JsonResponse({"response_code": 3, "error_msg": DUPLICATE_MEMBER_ENTRY})

    elif method == "edit":
        try:
            old_member = Member.objects.get(server_primary_key=member_id)
            old_member.last_name = last_name
            old_member.card_number = card_number
            old_member.save()
        except IntegrityError as e:
            if 'unique constraint' in e.args[0]:
                return JsonResponse({"response_code": 3, "error_msg": DUPLICATE_MEMBER_ENTRY})

    return JsonResponse({"response_code": 2})


# Menu Category Sync
def sync_menu_category_with_server():
    MenuCategory.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/menu_category/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['menu_categories']:
            new_menu_category = MenuCategory(name=item['name'], kind=item['kind'],
                                             server_primary_key=int(item['server_primary_key']))
            new_menu_category.save()

    print("Menu Category Synchronization Complete.")


# Menu Item Sync
def sync_menu_item_with_server():
    MenuItem.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/menu_item/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['menu_items']:
            menu_category_object = MenuCategory.objects.get(server_primary_key=item['menu_category_id'])
            new_menu_item = MenuItem(name=item['name'], price=item['price'],
                                     is_delete=item['is_deleted'], menu_category=menu_category_object,
                                     server_primary_key=int(item['server_primary_key']))
            new_menu_item.save()

    print("Menu Item Synchronization Complete.")


# Printer Sync
def sync_printer_with_server():
    Printer.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/printer/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['printers']:
            new_printer = Printer(name=item['name'], server_primary_key=int(item['server_primary_key']))
            new_printer.save()

    print("Printer Synchronization Complete.")


# Printer to Category Sync
def sync_printer_to_category_with_server():
    PrinterToCategory.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/printer_to_category/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['printer_to_category_data']:
            printer_object = Printer.objects.get(server_primary_key=item['printer_id'])
            menu_category_object = MenuCategory.objects.get(server_primary_key=item['menu_category_id'])
            new_printer_to_category = PrinterToCategory(printer=printer_object,
                                                        menu_category=menu_category_object)
            new_printer_to_category.save()

    print("Printer To Category Synchronization Complete.")


# Table Category Sync
def sync_table_category_with_server():
    TableCategory.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/table_category/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['table_categories']:
            new_table_category = TableCategory(name=item['name'],
                                               server_primary_key=int(item['server_primary_key']))
            new_table_category.save()

    print("Table Category Synchronization Complete.")


# Table Sync
def sync_table_with_server():
    Table.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/table/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['tables']:
            table_category_object = TableCategory.objects.get(server_primary_key=item['table_category_id'])
            new_table = Table(name=item['name'], category=table_category_object,
                              server_primary_key=int(item['server_primary_key']))
            new_table.save()

    print("Table Synchronization Complete.")


# Employee Sync
def sync_employee_with_server():
    Employee.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/employee/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['employees']:
            new_employee = Employee(phone=item['phone'], password=item['password'],
                                    server_primary_key=int(item['server_primary_key']))
            new_employee.save()

    print("Employee Synchronization Complete.")


# Branch Sync
def sync_branch_with_server():
    Branch.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/branch/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['branches']:
            new_branch = Branch(name=item['name'], start_working_time=item['start_working_time'],
                                end_working_time=item['end_working_time'],
                                server_primary_key=int(item['server_primary_key']))
            new_branch.save()

    print("Branch Synchronization Complete.")


# Cash Sync
def sync_cash_with_server():
    Cash.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/cash/0/%d/" % BRANCH_ID)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['cashes']:
            branch_object = Branch.objects.get(server_primary_key=item['branch_id'])
            new_cash = Cash(created_date_time=item['created_date_time'], ended_date_time=item['ended_date_time'],
                            employee=None, income_report=item['income_report'],
                            outcome_report=item['outcome_report'],
                            event_tickets=item['event_tickets'],
                            current_money_in_cash=item['current_money_in_cash'], branch=branch_object,
                            is_close=item['is_close'],
                            server_primary_key=int(item['server_primary_key']))
            new_cash.save()

    print("Cash Synchronization Complete.")


# Invoice Sale Sync
def sync_invoice_sale_with_server():
    InvoiceSales.objects.all().delete()
    Game.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/invoice_sale/")
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['invoices']:
            branch_object = Branch.objects.get(server_primary_key=item['branch_id'])
            cash_object = Cash.objects.get(server_primary_key=item['cash_id'])
            member_object = None
            if item['member_id']:
                member_object = Member.objects.get(server_primary_key=item['member_id'])
            table_object = Table.objects.get(server_primary_key=item['table_id'])
            new_invoice = InvoiceSales(
                factor_number=item['factor_number'],
                created_time=item['created_time'],
                settle_time=item['settle_time'],
                cash=item['cash'],
                pos=item['pos'],
                discount=item['discount'],
                employee_discount=item['employee_discount'],
                tax=item['tax'],
                tip=item['tip'],
                settlement_type=item['settlement_type'],
                guest_numbers=item['guest_numbers'],
                is_settled=item['is_settled'],
                total_price=item['total_price'],
                member=member_object,
                table=table_object,
                ready_for_settle=item['ready_for_settle'],
                cash_desk=cash_object,
                branch=branch_object,
                is_do_not_want_order=item['is_do_not_want_order'],
                game_state=item['game_state'],
                server_primary_key=item['server_primary_key']
            )
            new_invoice.save()
            for game in item['games_list']:
                game_member_object = Member.objects.get(server_primary_key=game['member_id'])
                new_game = Game(
                    member=game_member_object,
                    start_time=game['start_time'],
                    end_time=game['end_time'],
                    numbers=game['numbers'],
                    points=game['points'],
                    add_date=game['add_date'],
                    server_primary_key=game['server_primary_key_game']
                )
                new_game.save()
                new_invoice_to_game = InvoicesSalesToGame(
                    invoice_sales=new_invoice,
                    game=new_game,
                    server_primary_key=game['server_primary_key_invoice_to_game']
                )
                new_invoice_to_game.save()

            for menu_item in item['menu_items_list']:
                menu_item_object = MenuItem.objects.get(server_primary_key=menu_item['menu_item_id'])
                new_invoice_to_menu_item = InvoicesSalesToMenuItem(
                    invoice_sales=new_invoice,
                    menu_item=menu_item_object,
                    numbers=menu_item['numbers'],
                    description=menu_item['description'],
                    is_print=menu_item['is_print'],
                    server_primary_key=menu_item['server_primary_key_invoice_to_menu_item']
                )
                new_invoice_to_menu_item.save()

    print("Invoice Sale Synchronization Complete.")


# Cash Sync
def sync_reserve_with_server():
    Reservation.objects.all().delete()
    branch_object = Branch.objects.all().first()
    response = request_handler("GET", BASE_URL + "api/offline/list/reserve/%d/" % branch_object.server_primary_key)
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['reserves']:
            branch_object = Branch.objects.get(server_primary_key=item['branch_id'])
            new_reserve = Reservation(
                start_time=item['start_time'],
                end_time=item['end_time'],
                numbers=item['numbers'],
                reserve_date=item['reserve_date'],
                customer_name=item['customer_name'],
                phone=item['phone'],
                reserve_state=item['reserve_state'],
                branch=branch_object,
                server_primary_key=item['server_primary_key']
            )
            new_reserve.save()
            for reserve_to_table in item['tables']:
                table_object = Table.objects.get(server_primary_key=reserve_to_table['table_id'])
                new_reserve_to_table = ReserveToTables(
                    reserve=new_reserve,
                    table=table_object,
                    server_primary_key=reserve_to_table['server_primary_key_reserve_to_table']
                )
                new_reserve_to_table.save()

    print("Reserve Synchronization Complete.")


@csrf_exempt
def create_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    start_time = rec_data.get('start_time')
    end_time = rec_data.get('end_time')
    reserve_date = rec_data.get('reserve_date')
    customer_name = rec_data.get('customer_name')
    tables_id = rec_data.get('tables_id')
    reserve_id = rec_data.get('reserve_id')
    numbers = rec_data.get('numbers')
    phone = rec_data.get('phone')
    reserve_state = rec_data.get('reserve_state')
    branch_id = rec_data.get('branch')
    reserve_id_server_primary_key = rec_data.get('server_primary_key_for_offline')

    if not start_time:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not len(tables_id):
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not reserve_state:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not reserve_date:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not numbers:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    if reserve_state != "walked":
        if not customer_name:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
        if not phone:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    else:
        customer_name = "حضوری"
        phone = "NO_PHONE"

    try:
        start_time_detail = datetime.strptime(start_time, "%H:%M")
        if not end_time:
            end_time_detail = start_time_detail + timedelta(minutes=120)
            end_time = end_time_detail.strftime("%H:%M")

        end_time_obj = datetime.strptime(end_time, "%H:%M")

        reserve_date_split = reserve_date.split('/')
        reserve_date_g = jdatetime.date(int(reserve_date_split[2]), int(reserve_date_split[1]),
                                        int(reserve_date_split[0])).togregorian()

    except ValueError:
        return JsonResponse({"response_code": 3, "error_msg": TIME_NOT_IN_CORRECT_FORMAT})
    if reserve_id == 0:
        branch_obj = Branch.objects.get(server_primary_key=branch_id)
        new_reservation = Reservation(
            start_time=datetime.strptime(start_time, "%H:%M"),
            end_time=end_time_obj,
            numbers=numbers,
            customer_name=customer_name,
            reserve_date=reserve_date_g,
            reserve_state=reserve_state,
            phone=phone,
            branch=branch_obj,
            server_primary_key=reserve_id_server_primary_key
        )
        new_reservation.save()
        for table_id in tables_id:
            table_obj = Table.objects.get(server_primary_key=table_id)
            new_reserve_to_table = ReserveToTables(
                table=table_obj,
                reserve=new_reservation,
                server_primary_key=0
            )
            new_reserve_to_table.save()

        return JsonResponse({"response_code": 2})
    else:
        old_reserve = Reservation.objects.get(server_primary_key=reserve_id_server_primary_key)
        old_reserve.start_time = start_time
        old_reserve.end_time = end_time
        old_reserve.numbers = numbers
        old_reserve.customer_name = customer_name
        old_reserve.phone = phone
        old_reserve.save()

        ReserveToTables.objects.filter(reserve=old_reserve).delete()
        for table_id in tables_id:
            table_obj = Table.objects.get(server_primary_key=table_id)
            new_reserve_to_table = ReserveToTables(
                table=table_obj,
                reserve=old_reserve,
                server_primary_key=0
            )
            new_reserve_to_table.save()
        return JsonResponse({"response_code": 2})


@csrf_exempt
def arrive_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    reserve_id = rec_data['reserve_id']
    if not reserve_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    old_reserve = Reservation.objects.get(server_primary_key=reserve_id)
    old_reserve.reserve_state = "arrived"
    old_reserve.save()
    return JsonResponse({"response_code": 2})


@csrf_exempt
def delete_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    reserve_id = rec_data['reserve_id']

    if not reserve_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    Reservation.objects.get(server_primary_key=reserve_id).delete()
    return JsonResponse({"response_code": 2})


@csrf_exempt
def add_waiting_list(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    start_time = rec_data['start_time']
    end_time = rec_data['end_time']
    reserve_date = rec_data['reserve_date']
    customer_name = rec_data['customer_name']
    numbers = rec_data['numbers']
    phone = rec_data['phone']
    reserve_state = rec_data['reserve_state']
    branch_id = rec_data['branch']
    reserve_id = rec_data['reserve_id']

    if not reserve_state or reserve_state != "call_waiting" or not customer_name or not reserve_date or not numbers \
            or not phone or not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    if start_time:
        start_time_detail = datetime.strptime(start_time, "%H:%M")
    else:
        start_time = "00:00"
        start_time_detail = datetime.strptime("00:00", "%H:%M")

    if not end_time:
        end_time_detail = start_time_detail + timedelta(minutes=120)
        end_time = end_time_detail.strftime("%H:%M")

    end_time_obj = datetime.strptime(end_time, "%H:%M")

    reserve_date_split = reserve_date.split('/')
    reserve_date_g = jdatetime.date(int(reserve_date_split[2]), int(reserve_date_split[1]),
                                    int(reserve_date_split[0])).togregorian()

    branch_obj = Branch.objects.get(server_primary_key=branch_id)
    new_reservation = Reservation(
        start_time=datetime.strptime(start_time, "%H:%M"),
        end_time=end_time_obj,
        numbers=numbers,
        customer_name=customer_name,
        reserve_date=reserve_date_g,
        reserve_state=reserve_state,
        phone=phone,
        branch=branch_obj,
        server_primary_key=reserve_id
    )
    new_reservation.save()

    return JsonResponse({"response_code": 2})


@csrf_exempt
def create_new_invoice_sales(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_sales_id = rec_data['invoice_sales_id']
    invoice_sales_server_primary_key = rec_data['invoice_sales_server_primary_key']
    invoice_sales_current_created_game_server_primary_key = rec_data[
        'invoice_sales_current_created_game_server_primary_key']
    new_game_id = 0
    table_id = rec_data.get('table_id')
    member_id = rec_data.get('member_id')
    guest_numbers = rec_data.get('guest_numbers')
    current_game = rec_data.get('current_game')
    menu_items_new = rec_data.get('menu_items_new')
    branch_id = rec_data.get('branch_id')
    cash_id = rec_data.get('cash_id')
    discount = rec_data.get('discount')
    tip = rec_data.get('tip')
    if tip == "" or discount == "":
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    member_obj = None
    if member_id:
        member_obj = Member.objects.get(server_primary_key=member_id)

    table_obj = Table.objects.get(server_primary_key=table_id)

    if invoice_sales_id == 0:
        if not table_id:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

        if not guest_numbers and not guest_numbers == 0:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

        cash_obj = Cash.objects.get(server_primary_key=cash_id)

        branch_obj = Branch.objects.get(server_primary_key=branch_id)

        new_invoice = InvoiceSales(
            branch=branch_obj,
            table=table_obj,
            guest_numbers=guest_numbers,
            member=member_obj,
            created_time=datetime.now(),
            cash_desk=cash_obj,
            discount=discount,
            tip=tip,
            server_primary_key=invoice_sales_server_primary_key
        )
        new_invoice.save()
        if current_game['start_time']:
            new_game = Game(
                member=member_obj,
                start_time=datetime.strptime(current_game['start_time'], '%H:%M'),
                add_date=datetime.now(),
                numbers=current_game['numbers'],
                server_primary_key=invoice_sales_current_created_game_server_primary_key
            )
            new_game.save()
            new_invoice_to_game = InvoicesSalesToGame(
                game=new_game,
                invoice_sales=new_invoice,
                server_primary_key=0
            )
            new_invoice_to_game.save()
            new_invoice.game_state = "PLAYING"
        for item in menu_items_new:
            item_obj = MenuItem.objects.get(server_primary_key=item['id'])
            new_item_to_invoice = InvoicesSalesToMenuItem(
                invoice_sales=new_invoice,
                menu_item=item_obj,
                numbers=item['nums'],
                description=item['description'],
                server_primary_key=0
            )
            new_item_to_invoice.save()
            new_invoice.total_price += int(item_obj.price) * int(item['nums'])

        new_invoice.save()

        return JsonResponse({"response_code": 2})

    elif invoice_sales_id != 0:
        old_invoice = InvoiceSales.objects.get(server_primary_key=invoice_sales_server_primary_key)
        old_invoice.table = table_obj
        old_invoice.guest_numbers = guest_numbers
        old_invoice.member = member_obj

        if current_game['id'] == 0 and current_game['start_time']:
            new_game = Game(
                member=member_obj,
                start_time=datetime.strptime(current_game['start_time'], '%H:%M'),
                add_date=datetime.now(),
                numbers=current_game['numbers'],
                server_primary_key=invoice_sales_current_created_game_server_primary_key
            )
            new_game.save()
            new_invoice_to_game = InvoicesSalesToGame(
                game=new_game,
                invoice_sales=old_invoice,
                server_primary_key=0
            )
            new_invoice_to_game.save()
            old_invoice.game_state = "PLAYING"

        for item in menu_items_new:
            item_obj = MenuItem.objects.get(server_primary_key=item['id'])
            new_item_to_invoice = InvoicesSalesToMenuItem(
                invoice_sales=old_invoice,
                menu_item=item_obj,
                numbers=item['nums'],
                description=item['description'],
                server_primary_key=0
            )
            new_item_to_invoice.save()
            old_invoice.total_price += int(item_obj.price) * int(item['nums'])

        old_invoice.discount = discount
        old_invoice.tip = tip
        old_invoice.save()

        return JsonResponse({"response_code": 2})


@csrf_exempt
def end_current_game(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    game_id = rec_data['game_id']
    end_time = datetime.now().time()

    if not game_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    game_object = Game.objects.get(server_primary_key=game_id, end_time="00:00:00")
    invoice_to_sales_object = InvoicesSalesToGame.objects.get(game=game_object)
    invoice_id = invoice_to_sales_object.invoice_sales.pk
    invoice_object = InvoiceSales.objects.get(pk=invoice_id)
    start_time = game_object.start_time
    game_object.end_time = end_time

    timedelta_start = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)

    timedelta_end = timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)

    t = timedelta_end - timedelta_start
    point = int(round(t.total_seconds() / 225))
    if game_object.member.card_number == "0000":
        if point % 16 != 0:
            point = (int(point / 16) + 1) * 16
    game_numbers = game_object.numbers

    game_object.points = point * game_numbers
    game_object.save()
    invoice_object.total_price += point * game_numbers * PRICE_PER_POINT_IN_GAME
    invoice_object.game_state = "END_GAME"
    invoice_object.save()
    return JsonResponse({"response_code": 2})


@csrf_exempt
def ready_for_settle(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']

    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    invoice_obj = InvoiceSales.objects.filter(server_primary_key=invoice_id).first()
    invoice_obj.ready_for_settle = True
    invoice_obj.save()
    return JsonResponse({"response_code": 2})


@csrf_exempt
def print_after_save(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']
    activate_is_print = rec_data['activate_is_print']
    invoice_obj = InvoiceSales.objects.get(server_primary_key=invoice_id)
    print_data = {
        'is_customer_print': 0,
        'invoice_id': invoice_obj.pk,
        'table_name': invoice_obj.table.name,
        'data': []
    }
    all_printers = Printer.objects.all().order_by("id")
    for printer in all_printers:
        print_data['data'].append({
            'printer_name': printer.name,
            'items': []
        })
    all_menu_item_invoice = InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice_obj, is_print=0)
    for menu_item in all_menu_item_invoice:
        printer_obj = PrinterToCategory.objects.filter(menu_category=menu_item.menu_item.menu_category)
        for printer in printer_obj:
            for real_printer in print_data['data']:
                if real_printer['printer_name'] == printer.printer.name:
                    real_printer['items'].append({
                        'name': menu_item.menu_item.name,
                        'numbers': menu_item.numbers,
                        'description': menu_item.description,
                        'price': int(menu_item.menu_item.price) * int(menu_item.numbers)
                    })
                    break

            if activate_is_print:
                menu_item.is_print = 1
                menu_item.save()

    return JsonResponse({"response_code": 2, 'printer_data': print_data})


@csrf_exempt
def delete_items(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']
    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    else:
        invoice_object = InvoiceSales.objects.get(server_primary_key=invoice_id)
        games = rec_data['game']
        menu_items_number_id = rec_data.get('menu_items_number_id')

        if not len(menu_items_number_id) and not len(games):
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

        for item_number_pair in menu_items_number_id:
            menu_item_id = item_number_pair[0]
            menu_item_numbers = item_number_pair[1]
            menu_item_object = MenuItem.objects.get(server_primary_key=menu_item_id)
            invoice_sale_to_menu_items_object = InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice_object,
                                                                                       menu_item=menu_item_object,
                                                                                       numbers=menu_item_numbers).first()
            invoice_sale_to_menu_items_object.delete()
            invoice_object.total_price -= int(menu_item_object.price) * int(menu_item_numbers)
            invoice_object.save()

        for game_id in games:
            game_obj = Game.objects.get(server_primary_key=game_id)
            invoice_object.total_price -= int(game_obj.points) * PRICE_PER_POINT_IN_GAME
            invoice_object.save()
            game_obj.delete()

        return JsonResponse({"response_code": 2})


@csrf_exempt
def delete_invoice(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']

    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    InvoiceSales.objects.get(server_primary_key=invoice_id).delete()

    return JsonResponse({"response_code": 2})


@csrf_exempt
def settle_invoice_sale(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": "GET REQUEST!"})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data.get('invoice_id')
    cash = rec_data.get('cash')
    pos = rec_data.get('card')
    if not invoice_id or (not pos and not pos == 0) or (not cash and not cash == 0):
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    invoice_object = InvoiceSales.objects.get(server_primary_key=invoice_id)
    invoice_object.is_settled = 1
    invoice_object.cash = int(cash)
    invoice_object.pos = int(pos)
    invoice_object.settle_time = datetime.now()
    invoice_object.save()

    return JsonResponse({"response_code": 2})


@csrf_exempt
def close_cash(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    now = datetime.now()
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

    branch_obj = Branch.objects.get(pk=branch_id)
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


@csrf_exempt
def open_cash(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch']
    cash_server_id = rec_data['cash_server_id']
    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch_obj = Branch.objects.get(server_primary_key=branch_id)
    Cash(branch=branch_obj, server_primary_key=cash_server_id).save()

    return JsonResponse({"response_code": 2})


sync_branch_with_server()
sync_members_with_server()
sync_menu_category_with_server()
sync_menu_item_with_server()
sync_printer_with_server()
sync_printer_to_category_with_server()
sync_table_category_with_server()
sync_table_with_server()
sync_employee_with_server()
sync_cash_with_server()
sync_invoice_sale_with_server()
sync_reserve_with_server()
