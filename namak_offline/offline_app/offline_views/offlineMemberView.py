from django.http import JsonResponse
import json
from offline_app.models import *
from django.db.models.functions import Concat
from django.db.models import Value as V
from django.db import IntegrityError
from offline_app.views import create_new_request_for_online_api
from namak_offline.settings import BASE_ONLINE_SERVER_API_URL

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


def add_member(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": "GET REQUEST!"})

    rec_data = json.loads(request.read().decode('utf-8'))
    member_id = rec_data.get('member_id')
    first_name = rec_data.get('first_name')
    last_name = rec_data.get('last_name')
    card_number = rec_data.get('card_number')
    card_number = card_number.replace("؟", "")
    card_number = card_number.replace("٪", "")
    card_number = card_number.replace("?", "")
    card_number = card_number.replace("%", "")
    year_of_birth = rec_data.get('year_of_birth')
    month_of_birth = rec_data.get('month_of_birth')
    day_of_birth = rec_data.get('day_of_birth')
    intro = rec_data.get('intro')
    phone = rec_data.get('phone')

    if not first_name:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not last_name:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not card_number:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not year_of_birth:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not month_of_birth:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not day_of_birth:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not phone:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
    if not intro:
        return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})

    if member_id == 0:
        try:
            new_member = Member(
                last_name=last_name,
                card_number=card_number,
                server_primary_key=0
            )
            new_member.save()

            if not create_new_request_for_online_api(BASE_ONLINE_SERVER_API_URL + "api/addMember/", "POST", rec_data):
                new_member.delete()
                return JsonResponse({"response_code": 3, "error_msg": SAVING_REQUEST_FOR_ONLINE_SERVER_PROBLEM})

        except IntegrityError as e:
            if 'unique constraint' in e.args[0]:
                return JsonResponse({"response_code": 3, "error_msg": DUPLICATE_MEMBER_ENTRY})

    return JsonResponse({"response_code": 2})


def get_members(request):
    if request.method != "GET":
        return JsonResponse({"response_code": 4, "error_msg": "GET REQUEST!"})

    members = Member.objects.all().order_by("-id")[:100]
    members_data = []
    for member in members:
        members_data.append({
            'id': member.pk,
            'last_name': member.last_name,
            'card_number': member.card_number,
            'server_primary_key': member.server_primary_key,
        })
    return JsonResponse({"response_code": 2, 'members': members_data})


def search_member(request):
    if request.method == "POST":
        rec_data = json.loads(request.read().decode('utf-8'))
        search_word = rec_data.get('search_word')
        username = rec_data.get('username')
        branch_id = rec_data.get('branch')

        if not search_word:
            return JsonResponse({"response_code": 3, "error_msg": DATA_REQUIRE})
        items_searched = Member.objects.annotate(
            full_name=Concat('first_name', V(' '), 'last_name')).filter(
            full_name__contains=search_word)
        members = []
        for member in items_searched:
            members.append({
                'id': member.pk,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'phone': member.phone,
                'card_number': member.card_number,
            })
        return JsonResponse({"response_code": 2, 'members': members})
    return JsonResponse({"response_code": 4, "error_msg": "GET REQUEST!"})


def get_member(request):
    if request.method != "POST":
        return JsonResponse({"response_code": 4, "error_msg": METHOD_NOT_ALLOWED})
    rec_data = json.loads(request.read().decode('utf-8'))
    if rec_data.get('member_id'):
        member_id = rec_data.get('member_id')
        member = Member.objects.get(pk=member_id)
        member_data = {
            'id': member.pk,
            'last_name': member.last_name,
            'card_number': member.card_number
        }
        return JsonResponse({"response_code": 2, 'member': member_data})

    if rec_data.get('card_number'):
        card_number = rec_data.get('card_number')
        card_number = card_number.replace("؟", "")
        card_number = card_number.replace("٪", "")
        card_number = card_number.replace("?", "")
        card_number = card_number.replace("%", "")
        member = Member.objects.filter(card_number=card_number).first()
        if member:
            member_data = {
                'id': member.pk,
                'last_name': member.last_name
            }
            return JsonResponse({"response_code": 2, 'member': member_data})
        else:
            return JsonResponse({"response_code": 3, 'error_msg': MEMBER_NOT_FOUND})
