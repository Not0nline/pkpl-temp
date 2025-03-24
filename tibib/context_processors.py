def auth_context(request):
    """Add authentication information to all templates."""
    is_authenticated = hasattr(request, 'user_id') or 'token' in request.session
    nama = getattr(request, 'nama', None) or request.session.get('nama', None)
    user_role = getattr(request, 'user_role', None) or request.session.get('user_role', None)
    phone_number = getattr(request, 'user_username', None) or request.session.get('phone_number', None)
    country_code = request.session.get('country_code', None)
    card_number = getattr(request, 'user_card_number', None) or request.session.get('card_number', None)
    
    context = {
        'is_authenticated': is_authenticated,
        'user_role': user_role,
        'user': {
            'is_authenticated': is_authenticated,
            'nama': nama,
            'role': user_role,
            'phone_number': phone_number,
            'country_code': country_code,
            'card_number': card_number
        }
    }
    return context
