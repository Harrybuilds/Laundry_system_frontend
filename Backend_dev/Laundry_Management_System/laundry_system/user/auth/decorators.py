from .auth_jwt import decode_token
from user.models import User
from functools import wraps
from django.http import JsonResponse


def auth_required(roles=None):
    if roles is None:
        roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if not auth_header.startswith('Bearer '):
                return JsonResponse({'error': 'Authorization header missing or malformed'}, status=401)

            token = auth_header.split(' ')[1]
            payload = decode_token(token)

            if not payload:
                return JsonResponse({'error': 'Token expired or Invalid token'}, status=401)
            
            email = payload.get('email')

            user = User.objects.filter(email=email).first()

            if user:
                request.user = user

                if roles and getattr(user, 'user_type', None) not in roles:
                    return JsonResponse({'error': 'Permission denied'}, status=403)
        
                return view_func(request, *args, **kwargs)
            else: return JsonResponse({'error': 'No such User'}, status=401)

        return wrapper
    return decorator

"""def role_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            
            if not user or not user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)

            user_role = getattr(user, 'user_type', None)

            if user_role not in allowed_roles:
                

            return view_func(request, *args, **kwargs)
        return wrapper

    return wrapper"""