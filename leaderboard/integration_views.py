import json
import uuid
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from django.db import models

from .models import Member, Reward, PointTransaction, RedemptionClaim
from .decorators import require_api_key
from .views import get_date_range, get_member_total_points
from .koha_utils import get_live_member_detail

@csrf_exempt
@require_api_key
@require_http_methods(["GET"])
def integration_member_detail(request, member_id):
    date_from, date_to = get_date_range(request)
    detail = get_live_member_detail(member_id, date_from, date_to)
    
    if not detail:
        return JsonResponse({'success': False, 'error': 'Member not found.'}, status=404)
        
    # Return structured data for integration
    return JsonResponse({
        'success': True,
        'data': {
            'member_id': detail['id'],
            'name': detail['name'],
            'role': detail['role'],
            'faculty': detail.get('faculty', ''),
            'department': detail.get('department', ''),
            'total_xp': detail['visits_total'],
            'total_books': detail['books_total'],
            'level': detail.get('level', {}).get('name', ''),
            'badges_count': len(detail.get('badges', [])),
            'badges': [{'name': b['name'], 'desc': b['desc']} for b in detail.get('badges', [])]
        }
    })

@csrf_exempt
@require_api_key
@require_http_methods(["POST"])
def integration_add_points(request, member_id):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)
        
    amount = data.get('amount')
    description = data.get('description', 'Manual API Add')
    
    if not amount or not isinstance(amount, (int, float)):
        return JsonResponse({'success': False, 'error': 'Amount must be a number.'}, status=400)
        
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        return JsonResponse({'success': False, 'error': 'Member not found in local DB. Cannot add local points to unknown member.'}, status=404)
        
    PointTransaction.objects.create(
        cardnumber=member_id,
        amount=amount,
        transaction_type='other',
        description=f"[API {request.api_key.name}] {description}"
    )
    
    # clear cache
    from django.core.cache import cache
    cache.clear()
    
    return JsonResponse({
        'success': True,
        'message': f'Successfully added {amount} XP to {member_id}.',
        'new_total_xp': get_member_total_points(member_id)
    })

@csrf_exempt
@require_api_key
@require_http_methods(["GET"])
def integration_rewards(request):
    rewards = Reward.objects.filter(is_active=True)
    data = []
    for r in rewards:
        data.append({
            'id': r.id,
            'name': r.name,
            'points_cost': r.points_cost,
            'stock': r.stock,
            'is_available': r.stock > 0
        })
    return JsonResponse({'success': True, 'data': data})

@csrf_exempt
@require_api_key
@require_http_methods(["POST"])
def integration_redeem(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body.'}, status=400)
        
    member_id = data.get('member_id', '').strip().upper()
    reward_id = data.get('reward_id')
    
    if not member_id or not reward_id:
        return JsonResponse({'success': False, 'error': 'member_id and reward_id are required.'}, status=400)
        
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        return JsonResponse({'success': False, 'error': 'Member not found.'}, status=404)
        
    reward = Reward.objects.filter(id=reward_id, is_active=True).first()
    if not reward:
        return JsonResponse({'success': False, 'error': 'Reward not found or inactive.'}, status=404)
        
    if reward.stock <= 0:
        return JsonResponse({'success': False, 'error': 'Reward is out of stock.'}, status=400)
        
    points = get_member_total_points(member_id)
    if points < reward.points_cost:
        return JsonResponse({'success': False, 'error': f'Insufficient points. Has {points}, needs {reward.points_cost}.'}, status=400)
        
    claim_code = f"API-REDEEM-{uuid.uuid4().hex[:6].upper()}"
    
    try:
        with transaction.atomic():
            PointTransaction.objects.create(
                cardnumber=member_id,
                amount=-reward.points_cost,
                transaction_type='redeem',
                description=f"API Redeem: {reward.name}"
            )
            
            reward.stock = models.F('stock') - 1
            reward.save()
            
            RedemptionClaim.objects.create(
                code=claim_code,
                member=member,
                reward=reward,
                status='pending'
            )
            
        from django.core.cache import cache
        cache.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'Redemption successful.',
            'claim_code': claim_code,
            'remaining_points': points - reward.points_cost
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
