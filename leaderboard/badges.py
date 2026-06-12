from .models import RedemptionClaim, SeminarRegistration

def get_pending_claims(request):
    count = RedemptionClaim.objects.filter(status='pending').count()
    return count if count > 0 else None

def get_pending_registrations(request):
    count = SeminarRegistration.objects.filter(status='registered').count()
    return count if count > 0 else None
