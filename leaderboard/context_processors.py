from django.conf import settings


def cas_settings(request):
    """Expose CAS config to all templates."""
    return {
        'CAS_LOCAL_DEV': getattr(settings, 'CAS_LOCAL_DEV', False),
        'CAS_SERVER_URL': getattr(settings, 'CAS_SERVER_URL', ''),
    }
