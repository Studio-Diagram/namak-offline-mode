from django.http import JsonResponse
import json
from offline_app.models import *
from datetime import timedelta
from datetime import datetime

WRONG_USERNAME_OR_PASS = "نام کاربری یا رمز عبور اشتباه است."
USERNAME_ERROR = 'نام کاربری خود  را وارد کنید.'
PASSWORD_ERROR = 'رمز عبور خود را وارد کنید.'
NOT_SIMILAR_PASSWORD = 'رمز عبور وارد شده متفاوت است.'
DATA_REQUIRE = "اطلاعات را به شکل کامل وارد کنید."
PHONE_ERROR = 'شماره تلفن خود  را وارد کنید.'
UNATHENTICATED = 'لطفا ابتدا وارد شوید.'
DUPLICATE_MEMBER_ENTRY = "شماره تلفن یا کارت تکراری است."
MEMBER_NOT_FOUND = "عضوی یافت نشد."
SAVING_REQUEST_FOR_ONLINE_SERVER_PROBLEM = "SAVING_REQUEST_FOR_ONLINE_SERVER_PROBLEM"
METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
IN_GAME = "در حال بازی"
END_GAME = "بازی تمام شده"
WAIT_GAME = "منتظر بازی"
ORDERED = "سفارش داده"
NOT_ORDERED = "سفارش نداده"
DO_NOT_WANT_ORDER = "سفارش ندارد"
DO_NOT_WANT_GAME = "بازی نمی‌خواهد"
NO_SHOP_PRODUCTS_IN_STOCK = "محصول فروشی در انبار نیست."
WAIT_FOR_SETTLE = "منتظر تسویه"
PRICE_PER_POINT_IN_GAME = 5000
PRICE_PER_HOUR_IN_GAME = 80000
SECONDS_PER_POINT = 225
CHUNKS_PER_HOUR = 16
GUEST_LAST_NAME = "مهمان"
GUEST_FIRST_NAME = "مهمان"


def get_invoice_sale_total_price(invoice_id):
    total_price = 0
    invoice_object = InvoiceSales.objects.get(pk=invoice_id)
    all_invoice_to_menu_items = InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice_object)
    for invoice_to_menu_item in all_invoice_to_menu_items:
        total_price += invoice_to_menu_item.numbers * int(invoice_to_menu_item.menu_item.price)

    all_invoice_sales_games = InvoicesSalesToGame.objects.filter(invoice_sales=invoice_object).exclude(game__points=0)
    for invoice_to_game in all_invoice_sales_games:
        total_price += invoice_to_game.game.points * PRICE_PER_POINT_IN_GAME

    return total_price


def get_menu_items_with_categories(request):
    if request.method != "GET":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    menu_items_with_categories_data = []
    menu_categories = MenuCategory.objects.all().order_by('list_order')
    for cat in menu_categories:
        menu_items = MenuItem.objects.filter(menu_category=cat, is_delete=0)
        menu_items_data = []
        for item in menu_items:
            menu_items_data.append({
                'id': item.pk,
                'name': item.name,
                'price': item.price
            })
        menu_items_with_categories_data.append({
            'category_name': cat.name,
            'items': menu_items_data,
        })
    return JsonResponse({"response_code": 2, 'menu_items_with_categories': menu_items_with_categories_data})


def get_menu_items(request):
    if request.method != "GET":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    all_menu_items = MenuItem.objects.filter(is_delete=0).order_by('menu_category__name')
    menu_items = []
    for item in all_menu_items:
        menu_items.append({
            "id": item.pk,
            "name": item.name,
            "price": item.price,
            "category_name": item.menu_category.name,
            "menu_category_id": item.menu_category.id
        })
    return JsonResponse({"response_code": 2, 'menu_items': menu_items})


def get_tables(request):
    if request.method != "GET":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    tables = Table.objects.all().order_by('id')
    tables_data = []
    for table in tables:
        tables_data.append({
            'table_id': table.pk,
            'table_name': table.name,
            'table_category_name': table.category.name,
            'is_checked': 0
        })
    return JsonResponse({"response_code": 2, 'tables': tables_data})


def get_all_today_invoices(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    cash_id = rec_data['cash_id']

    if not cash_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    cash_obj = Cash.objects.get(pk=cash_id)

    all_invoices = InvoiceSales.objects.filter(cash_desk=cash_obj, is_deleted=False).order_by(
        "is_settled")
    all_invoices_list = []
    for invoice in all_invoices:
        if invoice.settle_time:
            st_time = invoice.settle_time.time()
        else:
            st_time = 0

        invoice_to_menu_items = InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice).exclude(
            menu_item__menu_category__kind='OTHER')

        if invoice.ready_for_settle:
            invoice_status = {"status": "WAIT_FOR_SETTLE", "text": WAIT_FOR_SETTLE}
        else:
            if invoice_to_menu_items.count():
                invoice_status = {"status": "ORDERED", "text": ORDERED}
            else:
                if invoice.is_do_not_want_order:
                    invoice_status = {"status": "DO_NOT_WANT_ORDER", "text": DO_NOT_WANT_ORDER}
                else:
                    invoice_status = {"status": "NOT_ORDERED", "text": NOT_ORDERED}

        all_invoices_list.append({
            "invoice_id": invoice.pk,
            "guest_name": invoice.member.get_full_name() if invoice.member else GUEST_LAST_NAME,
            "table_name": invoice.table.name,
            "guest_nums": invoice.guest_numbers,
            "total_price": invoice.total_price,
            "discount": invoice.discount,
            "tip": invoice.tip,
            "settle_time": st_time,
            "is_settled": invoice.is_settled,
            "game_status": {"status": invoice.game_state, "text": invoice.get_game_state_display()},
            "invoice_status": invoice_status
        })
    return JsonResponse({"response_code": 2, "all_today_invoices": all_invoices_list})


def get_invoice(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']
    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    invoice_object = InvoiceSales.objects.get(pk=invoice_id)
    invoice_data = {
        'invoice_sales_id': invoice_object.pk,
        'table_id': invoice_object.table.pk,
        'table_name': invoice_object.table.name,
        'member_id': invoice_object.member.pk if invoice_object.member else 0,
        'guest_numbers': invoice_object.guest_numbers,
        'member_name': invoice_object.member.get_full_name() if invoice_object.member else GUEST_LAST_NAME,
        'member_data': invoice_object.member.get_full_name() if invoice_object.member else GUEST_LAST_NAME,
        'current_game': {
            'id': 0,
            'numbers': 0,
            'start_time': ''
        },
        'total_price': invoice_object.total_price,
        "discount": invoice_object.discount,
        "tip": invoice_object.tip,
        'menu_items_old': [],
        'shop_items_old': [],
        'games': [],
        'used_credit': 0,
        'total_credit': 0,
        'cash_amount': invoice_object.cash,
        "pos_amount": invoice_object.pos
    }
    invoice_games = InvoicesSalesToGame.objects.filter(invoice_sales=invoice_object)
    for game in invoice_games:
        if str(game.game.end_time) != "00:00:00":
            game_total_secs = (game.game.points / game.game.numbers * timedelta(seconds=225)).total_seconds()
            hour_points = int(game_total_secs / 3600)
            min_points = int((game_total_secs / 60) % 60)
            if len(str(hour_points)) == 1:
                hour_points_string = "0" + str(hour_points)
            else:
                hour_points_string = str(hour_points)

            if len(str(min_points)) == 1:
                min_points_string = "0" + str(min_points)
            else:
                min_points_string = str(min_points)

            invoice_data['games'].append({
                'id': game.game.pk,
                'numbers': game.game.numbers,
                'start_time': game.game.start_time.strftime('%H:%M'),
                'end_time': game.game.end_time.strftime('%H:%M'),
                'points': "%s:%s'" % (hour_points_string, min_points_string),
                'total': game.game.points * PRICE_PER_POINT_IN_GAME
            })
        elif str(game.game.end_time) == "00:00:00":
            invoice_data['current_game']['id'] = game.game.pk
            invoice_data['current_game']['numbers'] = game.game.numbers
            invoice_data['current_game']['start_time'] = game.game.start_time

    invoice_items = InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice_object)
    for item in invoice_items:
        invoice_data['menu_items_old'].append({
            'id': item.pk,
            'name': item.menu_item.name,
            'price': item.menu_item.price,
            'nums': item.numbers,
            'total': int(item.menu_item.price) * int(item.numbers),
            'description': item.description
        })

    return JsonResponse({"response_code": 2, "invoice": invoice_data})


def get_today_status(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    cash_id = rec_data['cash_id']

    cash_obj = Cash.objects.filter(pk=cash_id).first()

    if not cash_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    status = {
        "all_sales_price": 0,
        "all_cash": 0,
        "all_pos": 0,
        "all_guests": 0,
        "all_tax": 0,
        "all_discount": 0,
        "all_tip": 0,
        "all_bar": 0,
        "all_kitchen": 0,
        "all_other": 0,
        "all_games": 0
    }

    all_invoices = InvoiceSales.objects.filter(cash_desk=cash_obj, is_deleted=False)
    for invoice in all_invoices:
        status['all_sales_price'] += invoice.total_price
        status['all_cash'] += invoice.cash
        status['all_pos'] += invoice.pos
        status['all_guests'] += invoice.guest_numbers
        status['all_tax'] += invoice.tax
        status['all_discount'] += invoice.discount
        status['all_tip'] += invoice.tip
        all_invoice_menu_items = InvoicesSalesToMenuItem.objects.filter(invoice_sales=invoice)
        for invoice_to_menu_item in all_invoice_menu_items:
            if invoice_to_menu_item.menu_item.menu_category.kind == "BAR":
                status['all_bar'] += invoice_to_menu_item.numbers * int(invoice_to_menu_item.menu_item.price)
            elif invoice_to_menu_item.menu_item.menu_category.kind == "KITCHEN":
                status['all_kitchen'] += invoice_to_menu_item.numbers * int(invoice_to_menu_item.menu_item.price)
            elif invoice_to_menu_item.menu_item.menu_category.kind == "OTHER":
                status['all_other'] += invoice_to_menu_item.numbers * int(invoice_to_menu_item.menu_item.price)

        all_invoice_games = InvoicesSalesToGame.objects.filter(invoice_sales=invoice)
        for invoice_to_game in all_invoice_games:
            status['all_games'] += invoice_to_game.game.points * PRICE_PER_POINT_IN_GAME

    return JsonResponse({"response_code": 2, "all_today_status": status})


def create_new_invoice_sales(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_sales_id = rec_data['invoice_sales_id']
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
        member_obj = Member.objects.get(pk=member_id)

    table_obj = Table.objects.get(pk=table_id)

    if invoice_sales_id == 0:
        if not table_id:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

        if not guest_numbers and not guest_numbers == 0:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

        cash_obj = Cash.objects.get(pk=cash_id)

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
            server_primary_key=0
        )
        new_invoice.save()
        new_invoice_id = new_invoice.pk
        if current_game['start_time']:
            new_game = Game(
                member=member_obj,
                start_time=datetime.strptime(current_game['start_time'], '%H:%M'),
                add_date=datetime.now(),
                numbers=current_game['numbers'],
                server_primary_key=0
            )
            new_game.save()
            new_game_id = new_game.pk
            new_invoice_to_game = InvoicesSalesToGame(
                game=new_game,
                invoice_sales=new_invoice,
                server_primary_key=0
            )
            new_invoice_to_game.save()
            new_invoice.game_state = "PLAYING"
        for item in menu_items_new:
            item_obj = MenuItem.objects.get(pk=item['id'])
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
        valid_total_price = get_invoice_sale_total_price(new_invoice.id)
        if valid_total_price != new_invoice.total_price:
            new_invoice.total_price = valid_total_price
            new_invoice.save()

        return JsonResponse({"response_code": 2, "new_game_id": new_game_id, "new_invoice_id": new_invoice_id})

    elif invoice_sales_id != 0:
        old_invoice = InvoiceSales.objects.get(pk=invoice_sales_id)
        old_invoice.table = table_obj
        old_invoice.guest_numbers = guest_numbers
        old_invoice.member = member_obj

        if current_game['id'] == 0 and current_game['start_time']:
            new_game = Game(
                member=member_obj,
                start_time=datetime.strptime(current_game['start_time'], '%H:%M'),
                add_date=datetime.now(),
                numbers=current_game['numbers'],
                server_primary_key=0
            )
            new_game.save()
            new_game_id = new_game.pk
            new_invoice_to_game = InvoicesSalesToGame(
                game=new_game,
                invoice_sales=old_invoice,
                server_primary_key=0
            )
            new_invoice_to_game.save()
            old_invoice.game_state = "PLAYING"

        for item in menu_items_new:
            item_obj = MenuItem.objects.get(pk=item['id'])
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
        new_invoice_id = old_invoice.pk
        valid_total_price = get_invoice_sale_total_price(old_invoice.id)
        if valid_total_price != old_invoice.total_price:
            old_invoice.total_price = valid_total_price
            old_invoice.save()

        return JsonResponse({"response_code": 2, "new_game_id": new_game_id, "new_invoice_id": new_invoice_id})


def end_current_game(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    game_id = rec_data['game_id']
    end_time = datetime.now().time()

    if not game_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    game_object = Game.objects.get(pk=game_id, end_time="00:00:00")
    invoice_to_sales_object = InvoicesSalesToGame.objects.get(game=game_object)
    invoice_id = invoice_to_sales_object.invoice_sales.pk
    invoice_object = InvoiceSales.objects.get(pk=invoice_id)
    start_time = game_object.start_time
    game_object.end_time = end_time

    timedelta_start = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)

    timedelta_end = timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)

    t = timedelta_end - timedelta_start
    point = int(round(t.total_seconds() / 225))
    if not game_object.member:
        if point % 16 != 0:
            point = (int(point / 16) + 1) * 16
    game_numbers = game_object.numbers

    game_object.points = point * game_numbers
    game_object.save()
    invoice_object.total_price += point * game_numbers * PRICE_PER_POINT_IN_GAME
    invoice_object.game_state = "END_GAME"
    invoice_object.save()
    return JsonResponse({"response_code": 2})


def ready_for_settle(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']

    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    invoice_obj = InvoiceSales.objects.filter(id=invoice_id).first()
    invoice_obj.ready_for_settle = True
    invoice_obj.save()
    return JsonResponse({"response_code": 2})


def print_after_save(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']
    activate_is_print = rec_data['activate_is_print']
    invoice_obj = InvoiceSales.objects.get(pk=invoice_id)
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


def delete_items(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']
    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    else:
        invoice_object = InvoiceSales.objects.get(pk=invoice_id)
        menus = rec_data['menu']
        games = rec_data['game']
        message = rec_data['message']
        if not message:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
        if not len(menus) and not len(games):
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

        for menu_id in menus:
            menu_item_obj = InvoicesSalesToMenuItem.objects.get(pk=menu_id)
            invoice_object.total_price -= int(menu_item_obj.menu_item.price) * int(menu_item_obj.numbers)
            invoice_object.save()
            menu_item_obj.delete()
        for game_id in games:
            game_obj = InvoicesSalesToGame.objects.get(pk=game_id)
            invoice_object.total_price -= int(game_obj.game.points) * PRICE_PER_POINT_IN_GAME
            invoice_object.save()
            game_obj.delete()

        return JsonResponse({"response_code": 2})


def delete_invoice(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    invoice_id = rec_data['invoice_id']
    description = rec_data['description']

    if not invoice_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    invoice_obj = InvoiceSales.objects.filter(id=invoice_id).first()
    invoice_obj.is_deleted = True
    invoice_obj.delete_description = description

    invoice_obj.save()
    return JsonResponse({"response_code": 2})
