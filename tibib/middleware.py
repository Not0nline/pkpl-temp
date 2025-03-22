import jwt
from django.conf import settings
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    """Middleware to authenticate users via JWT token."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"error": "Authorization header missing"}, status=401)

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
                request.user_id = payload["id"]  # Attach user ID to request
                request.user_username = payload['full_phone']
                request.user_role = payload['role']
            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token has expired"}, status=401)
            except jwt.InvalidTokenError as e:
                print("JWT Error:", str(e))
                return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
