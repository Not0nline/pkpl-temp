import jwt
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect

class JWTAuthenticationMiddleware:
    """Middleware to authenticate users via JWT token."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
        
        print("ini middle ware")
        auth_header = request.headers.get("Authorization")
        auth_cookie = request.COOKIES.get("jwt_token")

        if auth_header and not auth_header:
            return JsonResponse({"error": "Authorization header missing"}, status=401)

        # dari postman
        if auth_header and auth_header.startswith("Bearer "):
            print("auth_header",auth_header)
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
                return JsonResponse({"error": "Invalid token"}, status=401)
        # ini kalo dari frontend
        elif auth_cookie:
            token = auth_cookie
            token = auth_cookie.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
                request.user_id = payload["id"]  # Attach user ID to request
                request.user_username = payload['full_phone']
                request.user_role = payload['role']
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "cookie has expired"}, status=401)
            except jwt.InvalidTokenError as e:
                print("JWT Error:", str(e))
                return JsonResponse({"error": "Invalid cookie"}, status=401)

        return self.get_response(request)

class JWTBlacklistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]


            try:
                jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token has expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)