from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from tibib.utils import decrypt_and_verify

# @csrf_exempt  # Remove this if CSRF protection is handled properly
def create_reksadana(request):
    try:
        # Extract form data
        name = request.POST.get('name')
        initial_value = request.POST.get('nav')
        category_id = request.POST.get('category_id')
        kustodian_id = request.POST.get('kustodian_id')
        penampung_id = request.POST.get('penampung_id')
        risk_level = request.POST.get('tingkat_resiko')

        print(name, initial_value, category_id, kustodian_id, penampung_id, risk_level)
        
        # Validate form data
        if not all([name, initial_value, category_id, kustodian_id, penampung_id, risk_level]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        # Validate foreign keys
        try:
            category = CategoryReksadana.objects.get(id=category_id)
            kustodian = Bank.objects.get(id=kustodian_id)
            penampung = Bank.objects.get(id=penampung_id)
        except Exception as e:
            return JsonResponse({'error': f'Invalid selection: {str(e)}'}, status=400)
        except CategoryReksadana.DoesNotExist:
            return JsonResponse({"error": "Invalid category ID"}, status=400)
        except Bank.DoesNotExist:
            return JsonResponse({"error": "Invalid bank ID"}, status=400)

        # Create new Reksadana entry
        reksadana = Reksadana.objects.create(
            name=name,
            nav=float(initial_value),
            aum=0,
            tingkat_resiko=risk_level,
            category=category,
            kustodian=kustodian,
            penampung=penampung
        )
        return JsonResponse({"message": "Reksadana created successfully", "id": str(reksadana.id_reksadana)}, status=201)
    
    except Exception as e:
        return JsonResponse({"error": f"Failed to create reksadana : {str(e)}"}, status=500)
    
def edit_reksadana(request):
    try:
        # Extract form data
        id_reksadana = request.POST.get('reksadana_id')
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        kustodian_id = request.POST.get('kustodian_id')
        penampung_id = request.POST.get('penampung_id')
        risk_level = request.POST.get('tingkat_resiko')
        # Validate form data
        if not all([id_reksadana, name, category_id, kustodian_id, penampung_id, risk_level]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        # Validate foreign keys
        try:
            category = CategoryReksadana.objects.get(id=category_id)
            kustodian = Bank.objects.get(id=kustodian_id)
            penampung = Bank.objects.get(id=penampung_id)
        except Exception as e:
            return JsonResponse({'error': f'Invalid selection: {str(e)}'}, status=400)
        except CategoryReksadana.DoesNotExist:
            return JsonResponse({"error": "Invalid category ID"}, status=400)
        except Bank.DoesNotExist:
            return JsonResponse({"error": "Invalid bank ID"}, status=400)
        reksadana = Reksadana.objects.get(id_reksadana=id_reksadana)
        reksadana.name = name
        reksadana.category = category
        reksadana.kustodian = kustodian
        reksadana.penampung = penampung
        reksadana.tingkat_resiko = risk_level
        reksadana.save()
        return JsonResponse({'message':f'success on edit {reksadana.id_reksadana}:{reksadana.name} category:{reksadana.category.name} kustodian:{reksadana.kustodian.name} penampung:{reksadana.penampung.name}'}, status=201)
    except Exception as e:
        return JsonResponse({"error": f"Failed to edit reksadana : {str(e)} "}, status=405)
    

def fetch_all_reksadanas():
    return Reksadana.objects.all()

def get_all_reksadana(request):
    if request.method == "GET":
        reksadana_list = Reksadana.objects.all().values()
        return JsonResponse({"reksadanas": list(reksadana_list)}, status=200)

# @csrf_exempt
def create_unit_dibeli(request):
    if request.method == "POST":
        try:
            user_id = request.user_id
            data = json.loads(request.body)
            id_reksadana = data.get("id_reksadana")
            nominal = decrypt_and_verify(data.get("nominal"), data.get('signature'))
            print(type(nominal))

            if not user_id or not id_reksadana or not nominal:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Ensure Reksadana exists
            reksadana = get_object_or_404(Reksadana, id_reksadana=id_reksadana)

            unit = UnitDibeli.objects.create(
                user_id=user_id,
                id_reksadana=reksadana,
                nominal=nominal,
                waktu_pembelian = datetime.datetime.now()
            )

            return JsonResponse({"message": "Unit dibeli created", "unit_id": unit.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_units_by_user(request):
    if request.method == "GET":        
        # Get user_id from request
        user_id = request.user_id
        
        if not user_id:
            return JsonResponse({"error": "User not authenticated"}, status=401)
            
        # Get unit data
        units = UnitDibeli.objects.filter(user_id=user_id).values()
        return JsonResponse(list(units), safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=405)

def get_reksadana_history(request, id_reksadana):
    if request.method == "GET":
        reksadana = Reksadana.objects.get(id_reksadana=id_reksadana)
        reksadana.generate_made_up_history_per_hour()
        return JsonResponse(list(HistoryReksadana.objects.filter(id_reksadana=reksadana).values()), safe=False)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# def edit_reksadana(request):
#     try:
#         data = json.loads(request.body)
#         id_reksadana = data.get("id_reksadana")

#         category = CategoryReksadana.objects.get(id=data.get("category_id"))
#         kustodian = Bank.objects.get(id=data.get("kustodian_id"))
#         penampung = Bank.objects.get(id=data.get("penampung_id"))

    #     reksadana = Reksadana.objects.get(id_reksadana=id_reksadana)
    #     reksadana.name = data.get("name")
    #     reksadana.category = category
    #     reksadana.kustodian = kustodian
    #     reksadana.penampung = penampung
    #     reksadana.save()
    #     return JsonResponse({'message':f'success on edit {reksadana.id}:{reksadana.name} category:{reksadana.category_id} kustodian:{reksadana.kustodian_id} penampung:{reksadana.penampung_id}'})
    # except:
    #     return JsonResponse({"error": "Invalid request method"}, status=405)

# @csrf_exempt
def delete_unit_dibeli_by_id(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        id_unitdibeli = data.get("id_unitdibeli")
        if not id_unitdibeli:
            return JsonResponse({"error": "id_unitdibeli is required"}, status=400)

        unitdibeli = get_object_or_404(UnitDibeli, id=id_unitdibeli)
        if str(request.user_id) != str(unitdibeli.user_id):
            return JsonResponse({"error": "You are not authorized to delete this unit"}, status=403)

        unitdibeli.delete()
        return JsonResponse({"message": "UnitDibeli deleted successfully"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

def get_all_categories(request):
    """
    Get all Reksadana categories for dropdown selection
    """
    try:
        categories = CategoryReksadana.objects.all()
        return [{'id': category.id, 'name': category.name} for category in categories]
    except Exception as e:
        print(f"Error getting categories: {str(e)}")
        return []

def get_all_banks(request):
    """
    Get all Banks for dropdown selection
    """
    try:
        banks = Bank.objects.all()
        return [{'id': bank.id, 'name': bank.name} for bank in banks]
    except Exception as e:
        print(f"Error getting banks: {str(e)}")
        return []

# def create_reksadana_api(request):
#     """
#     Create a new Reksadana from form data (not JSON)
#     """
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#     try:
#         # Extract form data
#         name = request.POST.get('name')
#         description = request.POST.get('description')
#         initial_value = request.POST.get('initial_value')
#         category_id = request.POST.get('category_id')
#         kustodian_id = request.POST.get('kustodian_id')
#         penampung_id = request.POST.get('penampung_id')
        
#         # Validate form data
#         if not all([name, description, initial_value, category_id, kustodian_id, penampung_id]):
#             return JsonResponse({'error': 'All fields are required'}, status=400)
        
#         # Validate foreign keys
#         try:
#             category = CategoryReksadana.objects.get(id=category_id)
#             kustodian = Bank.objects.get(id=kustodian_id)
#             penampung = Bank.objects.get(id=penampung_id)
#         except Exception as e:
#             return JsonResponse({'error': f'Invalid selection: {str(e)}'}, status=400)
        
#         # Create new Reksadana entry
#         reksadana = Reksadana.objects.create(
#             name=name,
#             description=description,
#             nav=float(initial_value),
#             aum=0,  # Initial AUM is 0
#             tingkat_resiko="Konservatif",  # Default risk level
#             category=category,
#             kustodian=kustodian,
#             penampung=penampung
#         )
        
#         return JsonResponse({'success': 'Reksadana created successfully', 'id': reksadana.id}, status=201)
    
#     except Exception as e:
#         return JsonResponse({'error': f'Error creating Reksadana: {str(e)}'}, status=500)
    
    