import jwt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect

class JWTAuthenticationMiddleware:
    """Middleware to authenticate users via JWT token."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Mastiin url ini bisa di akses tanpa jwt token
        exempt_paths = [
            '/login/', 
            '/register/', 
            '/static/', 
            '/admin/',
            '/favicon.ico',
        ]

        current_path = request.path
        if any(current_path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization")

        token = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
                # Set user attributes on the request object
                request.user_id = payload.get("id")
                request.user_username = payload.get('full_phone')
                request.user_role = payload.get('role')
                
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
                
        return self.get_response(request)
