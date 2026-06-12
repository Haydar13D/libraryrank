from functools import wraps
from django.http import JsonResponse
from django.utils import timezone
from .models import APIKey

def require_api_key(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        x_api_key = request.META.get('HTTP_X_API_KEY', '')
        
        key = None
        if auth_header.startswith('Bearer '):
            key = auth_header.split('Bearer ')[1].strip()
        elif x_api_key:
            key = x_api_key.strip()
            
        if not key:
            return JsonResponse({'success': False, 'error': 'API Key is missing.'}, status=401)
            
        api_key_obj = APIKey.objects.filter(key=key, is_active=True).first()
        if not api_key_obj:
            return JsonResponse({'success': False, 'error': 'Invalid or inactive API Key.'}, status=403)
            
        # Update last used
        api_key_obj.last_used = timezone.now()
        api_key_obj.save(update_fields=['last_used'])
        
        request.api_key = api_key_obj
        return view_func(request, *args, **kwargs)
        
    return _wrapped_view
