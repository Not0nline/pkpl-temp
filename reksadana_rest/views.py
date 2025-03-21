from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import uuid
import json

@csrf_exempt  # Remove this if CSRF protection is handled properly
def create_reksadana(request):
    if request.method == "POST":

        try:
            data = json.loads(request.body)

            # Extract required fields
            name = data.get("name")
            category_id = data.get("category_id")
            kustodian_id = data.get("kustodian_id")
            penampung_id = data.get("penampung_id")
            nav = data.get("nav")
            aum = data.get("aum")
            tingkat_resiko = data.get("tingkat_resiko", "Konservatif")

            # Validate foreign keys
            category = CategoryReksadana.objects.get(id=category_id)
            kustodian = Bank.objects.get(id=kustodian_id)
            penampung = Bank.objects.get(id=penampung_id)

            # Create new Reksadana entry
            reksadana = Reksadana.objects.create(
                name=name,
                category=category,
                kustodian=kustodian,
                penampung=penampung,
                nav=nav,
                aum=aum,
                tingkat_resiko=tingkat_resiko
            )

            return JsonResponse({"message": "Reksadana created successfully", "id": str(reksadana.id_reksadana)}, status=201)

        except CategoryReksadana.DoesNotExist:
            return JsonResponse({"error": "Invalid category ID"}, status=400)
        except Bank.DoesNotExist:
            return JsonResponse({"error": "Invalid bank ID"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    #TODO bikin htmlnya
    return render(request, "beli_reksadana.html")

def get_all_reksadana(_):
    reksadana_list = Reksadana.objects.all().values()
    return JsonResponse({"reksadana": list(reksadana_list)}, status=200)

@csrf_exempt
def create_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            id_reksadana = data.get("id_reksadana")
            nominal = data.get("nominal")

            if not user_id or not id_reksadana or not nominal:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Ensure Reksadana exists
            reksadana = get_object_or_404(Reksadana, id_reksadana=id_reksadana)

            payment = Payment.objects.create(
                user_id=user_id,
                id_reksadana=reksadana,
                nominal=nominal
            )

            return JsonResponse({"message": "Payment created", "payment_id": payment.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_payments_by_user(request, user_id):
    if request.method == "GET":
        payments = Payment.objects.filter(user_id=user_id).values()
        return JsonResponse(list(payments), safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def create_unit_dibeli(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            id_reksadana = data.get("id_reksadana")
            nominal = data.get("nominal")

            if not user_id or not id_reksadana or not nominal:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Ensure Reksadana exists
            reksadana = get_object_or_404(Reksadana, id_reksadana=id_reksadana)

            unit = UnitDibeli.objects.create(
                user_id=user_id,
                id_reksadana=reksadana,
                nominal=nominal
            )

            return JsonResponse({"message": "Unit dibeli created", "unit_id": unit.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_units_by_user(request, user_id):
    if request.method == "GET":
        units = UnitDibeli.objects.filter(user_id=user_id).values()
        return JsonResponse(list(units), safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_reksadana_history(request, id_reksadana):
    if request.method == "GET":
        reksadana = Reksadana.objects.get(id_reksadana=id_reksadana)
        reksadana.generate_made_up_history_per_hour()
        return JsonResponse(list(HistoryReksadana.objects.filter(id_reksadana=reksadana).values()), safe=False)
    return JsonResponse({"error": "Invalid request method"}, status=405)