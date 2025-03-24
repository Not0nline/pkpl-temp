import jwt
from django.conf import settings
from django.http import JsonResponse
from django.urls import resolve, Resolver404
from django.shortcuts import redirect

class JWTAuthenticationMiddleware:
    """Middleware to authenticate users via JWT token."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #Mastiin url ini bisa di akses tanpa jwt token
        exempt_paths = [
            '/login/', 
            '/register/', 
            '/static/', 
            '/admin/',
            '/', 
            '/favicon.ico',
        ]

        current_path = request.path
        if any(current_path.startswith(path) for path in exempt_paths):
            return self.get_response(request)
        session_token = request.session.get('token')
        auth_header = request.headers.get("Authorization")
        
        # For API endpoints that require authentication
        if request.path.startswith('/api/'):
            if not auth_header and session_token:
                auth_header = session_token
                # Also set it in the request for downstream use
                request.META['HTTP_AUTHORIZATION'] = auth_header
            
            if not auth_header:
                return JsonResponse({"error": "Authorization header missing"}, status=401)

        # We'll try to process the token from either the header or session
        token = None
        
        # First try to get the token from the Authorization header
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        # If not in header, try to get from session
        elif session_token and session_token.startswith("Bearer "):
            token = session_token.split(" ")[1]
            # Also set it in the request for downstream use
            request.META['HTTP_AUTHORIZATION'] = session_token
            
        print("Final token to process:", token)
        
        # If we have a token, try to decode it and set user attributes
        if token:
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
                # Set user attributes on the request object
                request.user_id = payload.get("id")
                request.user_username = payload.get('full_phone')
                request.user_role = payload.get('role')
                request.user_card_number = payload.get('card_number')
                
                print(f"Setting user_id on request: {request.user_id}")
                print("Decoded payload:", payload)
                
                # Also ensure these are in the session
                request.session['user_id'] = payload["id"]
                request.session['phone_number'] = payload['full_phone']
                request.session['user_role'] = payload['role']
                if 'card_number' in payload:
                    request.session['card_number'] = payload['card_number']
                request.session.modified = True
                
            except jwt.ExpiredSignatureError:
                if request.path.startswith('/api/'):
                    return JsonResponse({"error": "Token has expired"}, status=401)
                else:
                    # For non-API routes, redirect to login
                    return redirect('login')
            except jwt.InvalidTokenError as e:
                print("JWT Error:", str(e))
                if request.path.startswith('/api/'):
                    return JsonResponse({"error": "Invalid token"}, status=401)
                else:
                    # For non-API routes, redirect to login
                    return redirect('login')
        # For regular pages, check if we have user info from the token
        # If not and we're not on an exempt path, redirect to login
        elif not hasattr(request, 'user_id') and not any(request.path.startswith(path) for path in exempt_paths):
            return redirect('login')
        return self.get_response(request)
