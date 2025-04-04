from django.shortcuts import redirect, render
from reksadana_rest.models import Reksadana
from reksadana_rest.views import create_reksadana, edit_reksadana, get_all_categories, get_all_banks, fetch_all_reksadanas
import json

def handle_error(request, status_code, error_message, back_url=None):
    context = {
        'error': f"{status_code} - {error_message}",
        'status_code': status_code,
        'back_url': back_url or '/'
    }
    return render(request, "error.html", context, status=status_code)

def show_dashboard(request):
    if request.user_role != 'staff':
        return handle_error(request, 403, "Forbidden: You don't have permission to access this page")
    
    try:
        reksadanas = fetch_all_reksadanas()
        context = {
            "reksadanas": reksadanas,
            'user_role': 'staff'
        }
        return render(request, "dashboard_admin.html", context)
    except Exception as e:
        return handle_error(request, 500, f"Internal Server Error: {str(e)}")

def create_reksadana_staff(request):
    if request.user_role != 'staff':
        return handle_error(request, 403, "Forbidden: Staff privileges required")
    
    if request.method == 'POST':
        try:
            create_response = create_reksadana(request)
            if create_response.status_code == 201:
                return redirect('/staff/dashboard/')
            
            error_data = json.loads(create_response.content)
            return handle_error(
                request,
                create_response.status_code,
                error_data.get('error', 'Failed to create investment product'),
                back_url='/staff/create/'
            )
            
        except json.JSONDecodeError:
            return handle_error(request, 500, "Invalid server response format")
        except Exception as e:
            return handle_error(request, 500, f"Server Error: {str(e)}")
    
    try:
        context = {
            'categories': get_all_categories(request),
            'banks': get_all_banks(request),
            'user_role': 'staff'
        }
        return render(request, "create_reksadana.html", context)
    except Exception as e:
        return handle_error(request, 500, f"Failed to load form: {str(e)}")

def edit_reksadana_staff(request):
    if request.user_role != 'staff':
        return handle_error(request, 403, "Forbidden: Staff privileges required")
    
    # Get reksadana_id from both GET and POST methods
    reksadana_id = request.GET.get('reksadana_id') or request.POST.get('reksadana_id')
    if not reksadana_id:
        return handle_error(request, 400, "Bad Request: Missing investment product ID")
    
    try:
        reksadana = Reksadana.objects.get(id_reksadana=reksadana_id)
    except Reksadana.DoesNotExist:
        return handle_error(request, 404, "Investment product not found")
    except ValueError:
        return handle_error(request, 400, "Invalid product ID format")
    
    if request.method == 'POST':
        try:
            edit_response = edit_reksadana(request)
            if edit_response.status_code == 200:
                return redirect('/staff/dashboard/')
            
            error_data = json.loads(edit_response.content)
            return handle_error(
                request,
                edit_response.status_code,
                error_data.get('error', 'Failed to update investment product'),
                back_url=f'/staff/edit/?reksadana_id={reksadana_id}'
            )
            
        except json.JSONDecodeError:
            return handle_error(request, 500, "Invalid server response format")
        except Exception as e:
            return handle_error(request, 500, f"Server Error: {str(e)}")
    
    try:
        context = {
            'reksadana': reksadana,
            'categories': get_all_categories(request),
            'banks': get_all_banks(request),
            'user_role': 'staff'
        }
        return render(request, "edit_reksadana.html", context)
    except Exception as e:
        return handle_error(request, 500, f"Failed to load edit form: {str(e)}")