from django.http import JsonResponse
import json
from offline_app.models import *
from datetime import timedelta, datetime
import jdatetime

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
TIME_NOT_IN_CORRECT_FORMAT = 'زمان را به حالت درستی وارد کنید.'


def get_working_time_for_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch']

    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch = Branch.objects.get(server_primary_key=branch_id)

    start_time = datetime.strptime(branch.start_working_time.strftime("%H:%M"), "%H:%M")
    end_time = datetime.strptime(branch.end_working_time.strftime("%H:%M"), "%H:%M") + timedelta(minutes=15)
    working_data = []

    while start_time.time() != end_time.time():
        if start_time.strftime("%M") == '00':
            working_data.append({
                'time': start_time.strftime("%H:%M"),
                'hour': start_time.strftime("%H"),
                'minute': start_time.strftime("%M"),
                'is_hour': 1
            })
        else:
            working_data.append({
                'time': start_time.strftime("00:%M"),
                'hour': start_time.strftime("%H"),
                'minute': start_time.strftime("%M"),
                'is_hour': 0
            })
        start_time = datetime.strptime(start_time.strftime("%H:%M"), "%H:%M") + timedelta(minutes=15)

    return JsonResponse({"response_code": 2, 'working_data': working_data})


def get_today_for_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch']

    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch = Branch.objects.get(server_primary_key=branch_id)
    now = datetime.now()
    now_time = now.time()
    now_date = datetime.now().date()

    end_work_time = branch.end_working_time

    after_midnight_hours = ['00', '01', '02', '03', '04', '05', '06']

    end_work_time_hour = end_work_time.strftime('%H')
    if now_time < end_work_time and end_work_time_hour in after_midnight_hours:
        yesterday = now_date - timedelta(1)
        today = jdatetime.date.fromgregorian(day=yesterday.day, month=yesterday.month,
                                             year=yesterday.year)
        tomorrow = today + timedelta(days=1)
        tomorrow = tomorrow.strftime("%d/%m/%Y")
        today = today.strftime("%d/%m/%Y")
    else:
        today = jdatetime.date.fromgregorian(day=now_date.day, month=now_date.month,
                                             year=now_date.year)

        tomorrow = today + timedelta(days=1)
        tomorrow = tomorrow.strftime("%d/%m/%Y")
        today = today.strftime("%d/%m/%Y")

    return JsonResponse({"response_code": 2, 'today_for_reserve': today, 'tomorrow_for_reserve': tomorrow})


def get_reserves(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch']
    date = rec_data['date']
    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not date:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch_obj = Branch.objects.get(server_primary_key=branch_id)
    reserve_date_split = date.split('/')
    reserve_date_g = jdatetime.date(int(reserve_date_split[2]), int(reserve_date_split[1]),
                                    int(reserve_date_split[0])).togregorian()
    all_today_reserves = Reservation.objects.filter(branch=branch_obj, reserve_date=reserve_date_g,
                                                    is_delete=0).exclude(
        reserve_state="call_waiting")
    reserves_data = []
    for reserve in all_today_reserves:
        tables_to_reserve = ReserveToTables.objects.filter(reserve=reserve)
        for table_reserve in tables_to_reserve:
            reserve_duration_revers = datetime.strptime(
                reserve.start_time.strftime("%H:%M"), '%H:%M') - datetime.strptime(
                reserve.end_time.strftime("%H:%M"), '%H:%M')
            midnight_time = datetime.strptime("00:00", "%H:%M")
            reserve_duration = midnight_time - reserve_duration_revers

            reserves_data.append({
                'id': reserve.pk,
                'customer_name': reserve.customer_name,
                'start_time_hour': reserve.start_time.strftime('%H'),
                'start_time_min': reserve.start_time.strftime('%M'),
                'duration_class_name': 'H%sM%s' % (
                    reserve_duration.strftime("%H"), reserve_duration.strftime("%M")),
                'numbers': reserve.numbers,
                'table_name': table_reserve.table.name,
                'reserve_state': reserve.reserve_state
            })
    return JsonResponse({"response_code": 2, 'all_today_reserves': reserves_data})


def get_waiting_list_reserves(request):
    if not request.method == "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})

    rec_data = json.loads(request.read().decode('utf-8'))
    branch_id = rec_data['branch']
    date = rec_data['date']
    if not branch_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not date:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    branch_obj = Branch.objects.get(server_primary_key=branch_id)
    reserve_date_split = date.split('/')
    reserve_date_g = jdatetime.date(int(reserve_date_split[2]), int(reserve_date_split[1]),
                                    int(reserve_date_split[0])).togregorian()
    all_today_reserves = Reservation.objects.filter(branch=branch_obj, reserve_date=reserve_date_g,
                                                    reserve_state="call_waiting", is_delete=0)
    reserves_data = []
    for reserve in all_today_reserves:
        reserves_data.append({
            'id': reserve.pk,
            'customer_name': reserve.customer_name,
            'start_time': reserve.start_time.strftime("%H:%M"),
            'numbers': reserve.numbers,
            'phone': reserve.phone
        })
    return JsonResponse({"response_code": 2, 'all_today_waiting_list': reserves_data})


def add_reserve(request):
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
            server_primary_key=0
        )
        new_reservation.save()
        for table_id in tables_id:
            table_obj = Table.objects.get(pk=table_id)
            new_reserve_to_table = ReserveToTables(
                table=table_obj,
                reserve=new_reservation,
                server_primary_key=0
            )
            new_reserve_to_table.save()

        return JsonResponse({"response_code": 2})
    else:
        old_reserve = Reservation.objects.get(pk=reserve_id)
        old_reserve.start_time = start_time
        old_reserve.end_time = end_time
        old_reserve.numbers = numbers
        old_reserve.customer_name = customer_name
        old_reserve.phone = phone
        old_reserve.save()

        ReserveToTables.objects.filter(reserve=old_reserve).delete()
        for table_id in tables_id:
            table_obj = Table.objects.get(pk=table_id)
            new_reserve_to_table = ReserveToTables(
                table=table_obj,
                reserve=old_reserve,
                server_primary_key=0
            )
            new_reserve_to_table.save()
        return JsonResponse({"response_code": 2})


def arrive_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    reserve_id = rec_data['reserve_id']
    if not reserve_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    old_reserve = Reservation.objects.get(pk=reserve_id)
    old_reserve.reserve_state = "arrived"
    old_reserve.save()
    return JsonResponse({"response_code": 2})


def delete_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    reserve_id = rec_data['reserve_id']

    if not reserve_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    old_reserve = Reservation.objects.get(pk=reserve_id)
    if old_reserve.server_primary_key:
        old_reserve.is_delete = 1
        old_reserve.save()
    else:
        old_reserve.delete()
    return JsonResponse({"response_code": 2})


def get_reserve(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    reserve_id = rec_data['reserve_id']

    if not reserve_id:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    old_reserve = Reservation.objects.get(pk=reserve_id)

    reserve_tables_id = []

    tables = Table.objects.all().order_by('id')
    tables_data = []
    for table in tables:
        tables_data.append({
            'table_id': table.pk,
            'table_name': table.name,
            'is_checked': 0
        })

    reserve_to_tables = ReserveToTables.objects.filter(reserve=old_reserve)
    for reserve_table in reserve_to_tables:
        reserve_tables_id.append(reserve_table.table.pk)
        for item in tables_data:
            if item['table_id'] == reserve_table.table.pk:
                item['is_checked'] = 1
                break
    reserve_data = {
        'reserve_id': old_reserve.pk,
        'numbers': old_reserve.numbers,
        'start_time': "%s:%s" % (old_reserve.start_time.hour, old_reserve.start_time.minute),
        'end_time': "%s:%s" % (old_reserve.end_time.hour, old_reserve.end_time.minute),
        'customer_name': old_reserve.customer_name,
        'phone': old_reserve.phone,
        'reserve_state': old_reserve.reserve_state,
        'tables_id': reserve_tables_id,
        'tables': tables_data,
    }

    return JsonResponse({"response_code": 2, "reserve_data": reserve_data})


def add_waiting_list(request):
    if not request.method != "POST":
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
        server_primary_key=0
    )
    new_reservation.save()

    return JsonResponse({"response_code": 2})