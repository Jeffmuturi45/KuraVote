from django.core.cache import cache
from django.utils import timezone
import time


def get_active_users():
    active_ids = cache.get('active_user_ids', set())
    active_list = []
    now = time.time()
    stale = set()

    for user_id in list(active_ids):
        data = cache.get(f'active_user_{user_id}')
        if data and (now - data['last_seen']) < 300:
            active_list.append(data)
        else:
            stale.add(user_id)

    # Clean up stale entries
    if stale:
        active_ids -= stale
        cache.set('active_user_ids', active_ids, timeout=300)

    return active_list


def active_election(request):
    from .models import Election
    try:
        election = Election.objects.get(
            status=Election.STATUS_ACTIVE
        )
    except Election.DoesNotExist:
        election = None
    return {
        'active_election':    election,
        'active_users_count': len(get_active_users()),
    }
