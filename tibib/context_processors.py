def auth_context(request):
    """Add authentication information to all templates."""
    is_authenticated = hasattr(request, 'user_id')
    nama = getattr(request, 'nama', None)
    user_role = getattr(request, 'user_role', None)
    phone_number = getattr(request, 'user_username', None)
    country_code = getattr(request, 'country_code', None)
    card_number = getattr(request, 'user_card_number', None)

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