from django.db import IntegrityError
from django.http import JsonResponse
from offline_app import models
import requests, json
from django.views.decorators.csrf import csrf_exempt

BASE_URL = "http://127.0.0.1:9001/"
METHODE_NOT_ALLOWED = "This method is not allowed."
PAYLOAD_EMPTY = "Payload is empty!"
DATA_REQUIRE = "Data required!"
DUPLICATE_MEMBER_ENTRY = "DUPLICATE_MEMBER_ENTRY"


def request_handler(method, url, payload=None):
    if method == "GET":
        r = requests.get(url)
        return json.loads(r.text), r.status_code
    elif method == "POST":
        r = requests.post(url, payload)
        return json.loads(r.text), r.status_code

def sync_members_with_server():
    models.Member.objects.all().delete()
    response = request_handler("GET", BASE_URL + "api/offline/list/member/0/")
    json_data = response[0]
    status_code = response[1]

    if status_code == 200:
        for item in json_data['members']:
            new_member = models.Member(last_name=item['last_name'], card_number=item['card_number'],
                                       server_primary_key=int(item['p_key']))
            new_member.save()

    print("Member Synchronization Complete.")


sync_members_with_server()


def create_new_request_for_online_api(api_url, method, payload):
    try:
        new_request = models.SavedUsedAPIs(
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
            new_member = models.Member(
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
            old_member = models.Member.objects.get(server_primary_key=member_id)
            old_member.last_name = last_name
            old_member.card_number = card_number
            old_member.save()
        except IntegrityError as e:
            if 'unique constraint' in e.args[0]:
                return JsonResponse({"response_code": 3, "error_msg": DUPLICATE_MEMBER_ENTRY})

    return JsonResponse({"response_code": 2})
